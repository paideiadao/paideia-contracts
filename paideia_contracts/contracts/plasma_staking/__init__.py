from ast import Dict
from dataclasses import dataclass
import os
from sortedcontainers import SortedSet
from ergo_python_appkit.appkit import getblok_plasma, ErgoAppKit, ErgoValueT
from ergo_python_appkit.ErgoContractBase import ErgoContractBase
from ergo_python_appkit.ErgoBox import ErgoBox
from ergo_python_appkit.ErgoTransaction import ErgoTransaction
import sigmastate
import scala
import java
from org.ergoplatform.appkit import ErgoId, ErgoValue, InputBox, ContextVar, ErgoType, Iso
from scala.collection import JavaConverters
import sys
from jpype import JImplements, JOverride, JObject, JClass, JImplementationFor, JProxy
from jpype.types import JInt, JLong, JByte
from scorex.crypto.authds import package
from sigmastate.Values import ErgoTree
from special.collection import CollBuilder

@dataclass
class PlasmaStakingConfig():
    nftId: str
    stakedTokenId: str
    emissionAmount: int
    emissionDelay: int
    cycleLength: int

class PlasmaStakingState:

    def __init__(
        self,
        plasmaStakingConfig: PlasmaStakingConfig, 
        plasmaParameters: getblok_plasma.PlasmaParameters = getblok_plasma.PlasmaParameters.default(), 
        plasmaMap: getblok_plasma.collections.PlasmaMap = None, 
        totalStaked: int = 0) -> None:
        self._totalStaked = totalStaked
        self._plasmaParameters = plasmaParameters
        self._nft = plasmaStakingConfig.nftId
        self._stakedToken = plasmaStakingConfig.stakedTokenId
        self._sortedKeys = SortedSet()
        if plasmaMap is None:
            self._plasmaMap = getblok_plasma.collections.PlasmaMap(
                                sigmastate.AvlTreeFlags.AllOperationsAllowed(),
                                plasmaParameters,
                                scala.Option.apply(None),
                                getblok_plasma.ByteConversion.convertsId(),
                                getblok_plasma.ByteConversion.convertsLongVal())
        else:
            self._plasmaMap = plasmaMap

    def stake(self, stakingKey: str, stakeAmount: int) -> getblok_plasma.collections.ProvenResult:
        self._totalStaked += stakeAmount
        self._sortedKeys.add(stakingKey)
        return self._plasmaMap.insert(self.toOpSeq([scala.Tuple2(ErgoId.create(stakingKey), stakeAmount)]))

    def getStake(self, stakingKey: str) -> int:
        return int(self.getStakes([stakingKey]).response().apply(JClass("java.lang.Object")@JInt(0)).tryOp().getOrElse(None).value())
        
    def unstake(self, stakingKey: str) -> getblok_plasma.collections.ProvenResult:
        stakeAmount = self.getStake(stakingKey)
        self._totalStaked -= stakeAmount
        self._sortedKeys.remove(stakingKey)
        return self._plasmaMap.delete(self.toOpSeq([ErgoId.create(stakingKey)]))

    def getStakes(self, stakingKeys: list[str]) -> getblok_plasma.collections.ProvenResult:
        return self._plasmaMap.lookUp(self.toOpSeq([ErgoId.create(key) for key in stakingKeys]))

    def changeStakes(self, newStakes: dict[str,int]) -> getblok_plasma.collections.ProvenResult:
        currentStakes = self.getStakes(list(newStakes.keys())).response()
        totalCurrentStake = 0
        for i in range(len(newStakes)):
            totalCurrentStake += int(currentStakes.apply(JClass("java.lang.Object")@JInt(i)).tryOp().getOrElse(None).value())
        totalNewStake = 0
        for newStake in newStakes.values():
            totalNewStake += newStake
        self._totalStaked = self._totalStaked - totalCurrentStake + totalNewStake
        return self._plasmaMap.update(self.toOpSeq([scala.Tuple2(ErgoId.create(key), newStakes[key]) for key in newStakes]))

    def getKeys(self, i: int = 0, n: int = 1) -> list[str]:
        return self._sortedKeys[i:i+n]

    def __len__(self):
        return len(self._sortedKeys)

    def toOpSeq(self, l: list):
        return JavaConverters.asScalaIteratorConverter(java.util.ArrayList(l).iterator()).asScala().toSeq()

class PlasmaStakingContract(ErgoContractBase):
    
    def __init__(self, appKit: ErgoAppKit) -> None:       
        super().__init__(appKit, script=os.path.join(os.path.dirname(__file__),f"ergoscript/latest/plasmaStaking.es"))

class PlasmaStakingBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, plasmaStakingConfig: PlasmaStakingConfig, nextSnapshot: int, stakers: PlasmaStakingState, stakerSnapshots: list[PlasmaStakingState], stakedTokenAmount: int) -> None:
        self._appKit = appKit
        self._plasmaStakingContract = PlasmaStakingContract(appKit)
        self._config = plasmaStakingConfig
        self._stakers = stakers
        self._stakerSnapshots = stakerSnapshots
        self._stakedTokenAmount = stakedTokenAmount
        tokens = {self._config.nftId: 1}
        if self._stakedTokenAmount > 0:
            tokens[self._config.stakedTokenId] = self._stakedTokenAmount
        super().__init__(appKit,int(1e6),self._plasmaStakingContract.contract,tokens,{})

        self._nextSnapshot = nextSnapshot
        self.updateRegisters()

    @staticmethod
    def fromInputBox(
        inputBox: InputBox, 
        plasmaStakingConfig: PlasmaStakingConfig, 
        plasmaStakingContract: PlasmaStakingContract,
        stakers: PlasmaStakingState,
        snapshots: list[PlasmaStakingState]) -> 'PlasmaStakingBox':
        _stakers = inputBox.getRegisters().get(0).getValue()
        if _stakers.digest() != stakers._plasmaMap.ergoValue().getValue().digest():
            print(f"_stakers.digest(): {_stakers.digest()}")
            print(f"stakers._plasmaMap.digest(): {stakers._plasmaMap.ergoValue().getValue().digest()}")
            raise Exception("AVLTree does not match local state")
        _params = inputBox.getRegisters().get(1).getValue()
        #_snapshots = inputBox.getRegisters().get(2).getValue()
        stakedTokenAmount = 0 if inputBox.getTokens().size() < 2 else inputBox.getTokens().get(1).getValue()
        return PlasmaStakingBox(
            appKit=plasmaStakingContract.appKit,
            plasmaStakingConfig=plasmaStakingConfig,
            nextSnapshot=_params.apply(3),
            stakedTokenAmount=stakedTokenAmount,
            stakers=stakers,
            stakerSnapshots=snapshots)

    @property
    def totalStaked(self) -> int:
        totalStaked = 0
        for key in self._stakers.getKeys(0,self.numberOfStakers):
            totalStaked += self._stakers.getStake(key)
        return totalStaked

    @property
    def numberOfStakers(self) -> int:
        return len(self._stakers)

    @property
    def nextSnapshot(self) -> int:
        return self._nextSnapshot
    @nextSnapshot.setter
    def nextSnapshot(self, nextSnapshot: int) -> None:
        self._nextSnapshot = nextSnapshot
        self.updateRegisters()

    def updateRegisters(self):
        snapshots = []
        for snapshot in self._stakerSnapshots:
            snapshots.append(ErgoValue.pairOf(scala.Tuple2(ErgoValue.of(JInt(len(snapshot._plasmaMap))),snapshot._plasmaMap.ergoValue())))
        self.registers = [
            self._stakers._plasmaMap.ergoValue(),
            ErgoAppKit.ergoValue([
                self._config.emissionAmount,
                self._config.emissionDelay,
                self._config.cycleLength,
                self.nextSnapshot,
                self.numberOfStakers,
                self.totalStaked
            ],ErgoValueT.LongArray)
        ]
        if len(snapshots) > 0:
            self.registers.append(ErgoValue.of(snapshots))

    def stake(self, stakingKey: str, amount: int) -> getblok_plasma.collections.ProvenResult:
        self._stakedTokenAmount += amount
        self.tokens[self._config.stakedTokenId] += amount
        returnVal = self._stakers.stake(stakingKey, amount)
        self.updateRegisters()
        return returnVal

    def addStake(self, key: str, amount: int) -> getblok_plasma.collections.ProvenResult:
        currentStake = self._stakers.getStake(key)
        self._stakedTokenAmount += amount
        self.tokens[self._config.stakedTokenId] += amount
        returnVal = self._stakers.changeStakes({key: currentStake+amount})
        self.updateRegisters()
        return returnVal

    def partialUnstake(self, key: str, amount: int) -> getblok_plasma.collections.ProvenResult:
        currentStake = self._stakers.getStake(key)
        if amount >= currentStake:
            raise Exception("Can not partially unstake more than current stake amount")
        self._stakedTokenAmount -= amount
        self.tokens[self._config.stakedTokenId] -= amount
        returnVal = self._stakers.changeStakes({key: currentStake-amount})
        self.updateRegisters()
        return returnVal

    def unstake(self, key: str) -> getblok_plasma.collections.ProvenResult:
        currentStake = self._stakers.getStake(key)
        self._stakedTokenAmount -= currentStake
        self.tokens[self._config.stakedTokenId] -= currentStake
        returnVal = self._stakers.unstake(key)
        self.updateRegisters()
        return returnVal

class StakeTransaction(ErgoTransaction):
    def __init__(
            self,
            plasmaStakingInput: InputBox,
            plasmaStakingContract: PlasmaStakingContract,
            plasmaStakingConfig: PlasmaStakingConfig,
            stakers: PlasmaStakingState,
            snapshots: list[PlasmaStakingState],
            address) -> None:
        super().__init__(plasmaStakingContract.appKit)
        plasmaStakingBox = PlasmaStakingBox.fromInputBox(
            inputBox=plasmaStakingInput,
            plasmaStakingConfig=plasmaStakingConfig,
            plasmaStakingContract=plasmaStakingContract,
            stakers=stakers,
            snapshots=snapshots
        )
        dummyUserInput = ErgoBox(
            appKit=plasmaStakingContract.appKit,
            value=int(1e6),
            contract=plasmaStakingContract.appKit.dummyContract(),
            tokens={plasmaStakingConfig.stakedTokenId: 100}
        ).inputBox()
        dummyUserOutput = plasmaStakingContract.appKit.mintToken(
            value=int(1e6),
            tokenId=plasmaStakingInput.getId().toString(),
            tokenName="Bla",
            tokenDesc="Bla",
            mintAmount=1,
            decimals=0,
            contract=plasmaStakingContract.appKit.dummyContract()
        )
        provenResult = plasmaStakingBox.stake(plasmaStakingInput.getId().toString(),100)
        print(provenResult)
        opList = [ErgoValue.pairOf(scala.Tuple2(
                        ErgoValue.of(getblok_plasma.ByteConversion.convertsId().convertToBytes(plasmaStakingInput.getId())),
                        ErgoValue.of(getblok_plasma.ByteConversion.convertsLongVal().convertToBytes(100))))
                    ]
        print(opList[0].getValue()._1())
        plasmaStakingInput = plasmaStakingInput.withContextVars(
            ContextVar.of(0,JByte(0)),
            ContextVar.of(1,
                ErgoValue.of(
                    [ErgoValue.pairOf(scala.Tuple2(
                        ErgoValue.of(getblok_plasma.ByteConversion.convertsId().convertToBytes(plasmaStakingInput.getId())),
                        ErgoValue.of(getblok_plasma.ByteConversion.convertsLongVal().convertToBytes(100))))
                    ]
                    ,ErgoType.pairType(ErgoType.collType(ErgoType.byteType()),ErgoType.collType(ErgoType.byteType()))
                )
            ),
            ContextVar.of(2,provenResult.proof().ergoValue())
        )
        self.inputs = [plasmaStakingInput,dummyUserInput]
        self.outputs = [plasmaStakingBox.outBox,dummyUserOutput]
        self.fee = int(1e6)
        self.changeAddress = address


appKit = ErgoAppKit("http://ergolui.com:9053","mainnet","https://api.ergoplatform.com/api/v1")

plasmaStakingContract = PlasmaStakingContract(appKit)

plasmaStakingConfig = PlasmaStakingConfig(
    nftId="29d6c2d943d7f5a2800095dba6b6168f1602d355480218f4a8a8c6575245a907",
    stakedTokenId="0cd8c9f416e5b1ca9f986a7f10a84191dfb85941619e49e53c0dc30ebf83324b",
    emissionAmount=100000,
    emissionDelay=10,
    cycleLength=3600000
)

plasmaStakingState = PlasmaStakingState(plasmaStakingConfig=plasmaStakingConfig)

plasmaInitial = PlasmaStakingBox(
    appKit=appKit,
    plasmaStakingConfig=plasmaStakingConfig,
    nextSnapshot=1000000,
    stakers=plasmaStakingState,
    stakerSnapshots=[],
    stakedTokenAmount=10000000
).inputBox()

unsignedStakeTransaction = StakeTransaction(
    plasmaStakingInput=plasmaInitial,
    plasmaStakingContract=plasmaStakingContract,
    plasmaStakingConfig=plasmaStakingConfig,
    stakers=plasmaStakingState,
    snapshots=[],
    address=appKit.dummyContract().toAddress().toString()
)

appKit.signTransaction(unsignedTx=unsignedStakeTransaction)

from ergo_python_appkit.appkit import getblok_plasma
import sigmastate
import scala
import java
from org.ergoplatform.appkit import ErgoId
from scala.collection import JavaConverters
import sys
from jpype import JImplements, JOverride, JObject, JClass, JImplementationFor, JProxy
from jpype.types import JInt, JLong
from scorex.crypto.authds import package

class PlasmaStakingState:

    def __init__(
        self, 
        plasmaParameters: getblok_plasma.PlasmaParameters = getblok_plasma.PlasmaParameters.default(), 
        plasmaMap: getblok_plasma.collections.PlasmaMap = None, 
        totalStaked: int = 0) -> None:
        self._totalStaked = totalStaked
        self._plasmaParameters = plasmaParameters
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
        return self._plasmaMap.insert(self.toOpSeq([scala.Tuple2(ErgoId.create(stakingKey), stakeAmount)]))

    def getStake(self, stakingKey: str) -> int:
        return int(self.getStakes([stakingKey]).response().apply(JClass("java.lang.Object")@JInt(0)).tryOp().getOrElse(None).value())
        
    def unstake(self, stakingKey: str) -> getblok_plasma.collections.ProvenResult:
        stakeAmount = self.getStake(stakingKey)
        self._totalStaked -= stakeAmount
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

    def toOpSeq(self, l: list):
        return JavaConverters.asScalaIteratorConverter(java.util.ArrayList(l).iterator()).asScala().toSeq()

plasmaStakingState = PlasmaStakingState()

cometID = "0cd8c9f416e5b1ca9f986a7f10a84191dfb85941619e49e53c0dc30ebf83324b"
plasmaStakingState.stake(cometID,100)
print(plasmaStakingState.getStake(cometID))
plasmaStakingState.changeStakes({cometID: 200})
print(plasmaStakingState.getStake(cometID))
print(plasmaStakingState.stake(cometID, 100))
print(plasmaStakingState.getStake(cometID))

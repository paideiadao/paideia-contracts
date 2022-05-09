from dataclasses import dataclass
from datetime import datetime
from hashlib import blake2b
import os
from time import time
from typing import Dict, List
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT
from paideia_contracts.contracts.ErgoBox import ErgoBox
from paideia_contracts.contracts.ErgoContractBase import ErgoContractBase

from org.ergoplatform.appkit import ErgoValue, InputBox
from sigmastate.Values import ErgoTree

from paideia_contracts.contracts.ErgoTransaction import ErgoTransaction

class InvalidInputBoxException(Exception): pass
class InvalidTransactionConditionsException(Exception): pass

@dataclass
class AssetsRequired:
    nErgRequired: int
    tokensRequired: Dict[str, int]

class PaideiaStakingContract(ErgoContractBase):
    def __init__(self, stakingConfig, script: str = None, mapping: Dict[str, ErgoValue] = {}, ergoTree: ErgoTree = None) -> None:
        self.config = stakingConfig
        super().__init__(self.config.appKit, script, mapping, ergoTree)

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, config) -> None:
        self._config = config

class StakeContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(stakingConfig.emissionNFT, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/stake.es"),mapping=mapping)
  
    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.config.stakeTokenId:
            return False
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        if registers[0].getValue().size() != 2:
            return False
        return super().validateInputBox(inBox)

class StakeStateContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakedTokenID": ErgoAppKit.ergoValue(stakingConfig.stakedTokenId, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakePoolNFT": ErgoAppKit.ergoValue(stakingConfig.stakePoolNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(stakingConfig.emissionNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeContractHash": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingConfig.stakeContract._ergoTree.bytesHex()), digest_size=32).digest(), ErgoValueT.ByteArray).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakeState.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.config.stakeStateNFT:
            return False
        registers = inBox.getRegisters()
        if len(registers) > 1:
            return False
        if registers[0].getValue().size() != 5:
            return False
        return super().validateInputBox(inBox)

class StakePoolContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakePool.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.config.stakePoolNFT:
            return False
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        if registers[0].getValue().size() != 1:
            return False
        return super().validateInputBox(inBox)

class EmissionContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeTokenID": ErgoAppKit.ergoValue(stakingConfig.stakeTokenId, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakedTokenID": ErgoAppKit.ergoValue(stakingConfig.stakedTokenId, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/emission.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.config.emissionNFT:
            return False
        registers = inBox.getRegisters()
        if len(registers) > 1:
            return False
        if registers[0].getValue().size() != 4:
            return False
        return super().validateInputBox(inBox)

class StakingIncentiveContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeTokenID": ErgoAppKit.ergoValue(stakingConfig.stakeTokenId, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(stakingConfig.emissionNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakePoolKey": ErgoAppKit.ergoValue(stakingConfig.stakePoolKey, ErgoValueT.ByteArrayFromHex).getValue(),
            "_dustCollectionReward": ErgoAppKit.ergoValue(stakingConfig.dustCollectionReward, ErgoValueT.Long).getValue(),
            "_dustCollectionMinerFee": ErgoAppKit.ergoValue(stakingConfig.dustCollectionMinerFee, ErgoValueT.Long).getValue(),
            "_emitReward": ErgoAppKit.ergoValue(stakingConfig.emitReward, ErgoValueT.Long).getValue(),
            "_emitMinerFee": ErgoAppKit.ergoValue(stakingConfig.emitMinerFee, ErgoValueT.Long).getValue(),
            "_baseCompoundReward": ErgoAppKit.ergoValue(stakingConfig.baseCompoundReward, ErgoValueT.Long).getValue(),
            "_baseCompoundMinerFee": ErgoAppKit.ergoValue(stakingConfig.baseCompoundMinerFee, ErgoValueT.Long).getValue(),
            "_variableCompoundReward": ErgoAppKit.ergoValue(stakingConfig.variableCompoundReward, ErgoValueT.Long).getValue(),
            "_variableCompoundMinerFee": ErgoAppKit.ergoValue(stakingConfig.variableCompoundMinerFee, ErgoValueT.Long).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakingIncentive.es"),mapping=mapping)

class StakeProxyContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingConfig.stakingIncentiveContract._ergoTree.bytesHex()), digest_size=32).digest(), ErgoValueT.ByteArray).getValue(),
            "_toStakingIncentive": ErgoAppKit.ergoValue(stakingConfig.proxyToStakingIncentive, ErgoValueT.Long).getValue(),
            "_executorReward": ErgoAppKit.ergoValue(stakingConfig.proxyExecutorReward, ErgoValueT.Long).getValue(),
            "_minerFee": ErgoAppKit.ergoValue(stakingConfig.proxyMinerFee, ErgoValueT.Long).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakeProxy.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        return super().validateInputBox(inBox)

class AddStakeProxyContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingConfig.stakingIncentiveContract._ergoTree.bytesHex()), digest_size=32).digest(), ErgoValueT.ByteArray).getValue(),
            "_toStakingIncentive": ErgoAppKit.ergoValue(stakingConfig.proxyAddToStakingIncentive, ErgoValueT.Long).getValue(),
            "_executorReward": ErgoAppKit.ergoValue(stakingConfig.proxyExecutorReward, ErgoValueT.Long).getValue(),
            "_minerFee": ErgoAppKit.ergoValue(stakingConfig.proxyMinerFee, ErgoValueT.Long).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/addStakeProxy.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        return super().validateInputBox(inBox)

class UnstakeProxyContract(PaideiaStakingContract):
    def __init__(self, stakingConfig) -> None:
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingConfig.stakingIncentiveContract._ergoTree.bytesHex()), digest_size=32).digest(), ErgoValueT.ByteArray).getValue(),
            "_toStakingIncentive": ErgoAppKit.ergoValue(stakingConfig.proxyToStakingIncentive, ErgoValueT.Long).getValue(),
            "_executorReward": ErgoAppKit.ergoValue(stakingConfig.proxyExecutorReward, ErgoValueT.Long).getValue(),
            "_minerFee": ErgoAppKit.ergoValue(stakingConfig.proxyMinerFee, ErgoValueT.Long).getValue()
        }
        super().__init__(stakingConfig,script=os.path.join(os.path.dirname(__file__),"ergoscript/unstakeProxy.es"),mapping=mapping)
    
    def validateInputBox(self, inBox: InputBox) -> bool:
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        return super().validateInputBox(inBox)

class EmissionBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, emissionContract: EmissionContract, emissionRemaining: int, amountStaked: int, checkpoint: int, stakers: int, emissionAmount: int) -> None:
        self.emissionContract = emissionContract
        tokens = {self.emissionContract.config.emissionNFT: 1}
        if emissionRemaining > 0:
            tokens[self.emissionContract.config.stakedTokenId] = emissionRemaining
        registers = [
            ErgoAppKit.ergoValue([
                amountStaked,
                checkpoint,
                stakers,
                emissionAmount
            ],ErgoValueT.LongArray)
        ]  

        super().__init__(appKit,int(1e6),emissionContract.contract,tokens,registers)

        self._emissionRemaining = emissionRemaining
        self._amountStaked = amountStaked
        self._checkpoint = checkpoint
        self._stakers = stakers
        self._emissionAmount = emissionAmount

    @staticmethod
    def fromInputBox(inputBox: InputBox, emissionContract: EmissionContract):
        registers = inputBox.getRegisters()
        amountStaked = int(registers[0].getValue().apply(0))
        checkpoint = int(registers[0].getValue().apply(1))
        stakers = int(registers[0].getValue().apply(2))
        emissionAmount = int(registers[0].getValue().apply(3))
        if len(inputBox.getTokens()) > 1:
            emissionRemaining = int(inputBox.getTokens()[1].getValue())
        else:
            emissionRemaining = 0
        return EmissionBox(
            appKit=emissionContract.appKit,
            emissionContract=emissionContract,
            amountStaked=amountStaked,
            checkpoint=checkpoint,
            stakers=stakers,
            emissionAmount=emissionAmount,
            emissionRemaining=emissionRemaining)

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.amountStaked,
                self.checkpoint,
                self.stakers,
                self.emissionAmount
            ],ErgoValueT.LongArray)
        ]  

    @property
    def emissionRemaining(self) -> int:
        return self._emissionRemaining
    @emissionRemaining.setter
    def emissionRemaining(self, emissionRemaining: int) -> None:
        self._emissionRemaining = emissionRemaining
        self.tokens[self.emissionContract.config.stakedTokenId] = emissionRemaining

    @property
    def amountStaked(self) -> int:
        return self._amountStaked
    @amountStaked.setter
    def amountStaked(self, amountStaked: int) -> None:
        self._amountStaked = amountStaked
        self.updateRegisters()

    @property
    def checkpoint(self) -> int:
        return self._checkpoint
    @checkpoint.setter
    def checkpoint(self, checkpoint: int) -> None:
        self._checkpoint = checkpoint
        self.updateRegisters()

    @property
    def stakers(self) -> int:
        return self._stakers
    @stakers.setter
    def stakers(self, stakers: int) -> None:
        self._stakers = stakers
        self.updateRegisters()

    @property
    def emissionAmount(self) -> int:
        return self._emissionAmount
    @emissionAmount.setter
    def emissionAmount(self, emissionAmount: int) -> None:
        self._emissionAmount = emissionAmount
        self.updateRegisters()

    @property
    def emissionContract(self) -> EmissionContract:
        return self._emissionContract
    @emissionContract.setter
    def emissionContract(self, emissionContract: EmissionContract) -> None:
        self._emissionContract = emissionContract

class StakeBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, stakeContract: StakeContract, checkpoint: int, stakeTime: int, amountStaked: int, stakeKey: str) -> None:
        if amountStaked < 10*10**stakeContract.config.stakedTokenDecimals:
            raise InvalidInputBoxException("Stake box needs more than 10 tokens")
        self.stakeContract = stakeContract
        tokens = {self.stakeContract.config.stakeTokenId: 1, self.stakeContract.config.stakedTokenId: amountStaked}
        registers = [
            ErgoAppKit.ergoValue([
                checkpoint,
                stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(stakeKey, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e6),stakeContract.contract,tokens,registers)

        self._amountStaked = amountStaked
        self._checkpoint = checkpoint
        self._stakeTime = stakeTime
        self._stakeKey = stakeKey

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeContract: StakeContract):
        registers = inputBox.getRegisters()
        checkpoint = int(registers[0].getValue().apply(0))
        stakeTime = int(registers[0].getValue().apply(1))
        amountStaked = int(inputBox.getTokens()[1].getValue())
        stakeKey = registers[1].toHex()[4:]
        return StakeBox(
            appKit=stakeContract.appKit,
            stakeContract=stakeContract,
            checkpoint=checkpoint,
            stakeTime=stakeTime,
            amountStaked=amountStaked,
            stakeKey=stakeKey)

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.checkpoint,
                self.stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(self.stakeKey, ErgoValueT.ByteArrayFromHex)
        ]   

    @property
    def stakeTime(self) -> int:
        return self._stakeTime
    @stakeTime.setter
    def stakeTime(self, stakeTime: int) -> None:
        self._stakeTime = stakeTime
        self.updateRegisters()

    @property
    def amountStaked(self) -> int:
        return self._amountStaked
    @amountStaked.setter
    def amountStaked(self, amountStaked: int) -> None:
        self._amountStaked = amountStaked
        self.tokens[self.stakeContract.config.stakedTokenId] = amountStaked

    @property
    def checkpoint(self) -> int:
        return self._checkpoint
    @checkpoint.setter
    def checkpoint(self, checkpoint: int) -> None:
        self._checkpoint = checkpoint
        self.updateRegisters()

    @property
    def stakeKey(self) -> str:
        return self._stakeKey
    @stakeKey.setter
    def stakeKey(self, stakeKey: str) -> None:
        self._stakeKey = stakeKey
        self.updateRegisters()

    @property
    def stakeContract(self) -> StakeContract:
        return self._stakeContract
    @stakeContract.setter
    def stakeContract(self, stakeContract: StakeContract) -> None:
        self._stakeContract = stakeContract

class StakeStateBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, stakeStateContract: StakeStateContract, checkpoint: int, checkpointTime: int, amountStaked: int, cycleDuration: int, stakers: int) -> None:
        self.stakeStateContract = stakeStateContract
        tokens = {self.stakeStateContract.config.stakeStateNFT: 1, self.stakeStateContract.config.stakeTokenId: int(1e9)-stakers}
        registers = [
            ErgoAppKit.ergoValue([
                amountStaked,
                checkpoint,
                stakers,
                checkpointTime,
                cycleDuration
            ],ErgoValueT.LongArray)
        ]  

        super().__init__(appKit,int(1e6),stakeStateContract.contract,tokens,registers)

        self._amountStaked = amountStaked
        self._checkpoint = checkpoint
        self._checkpointTime = checkpointTime
        self._cycleDuration = cycleDuration
        self._stakers = stakers

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeStateContact: StakeStateContract):
        registers = inputBox.getRegisters()
        amountStaked = int(registers[0].getValue().apply(0))
        checkpoint = int(registers[0].getValue().apply(1))
        stakers = int(registers[0].getValue().apply(2))
        checkpointTime = int(registers[0].getValue().apply(3))
        cycleDuration = int(registers[0].getValue().apply(4))
        return StakeStateBox(
            appKit=stakeStateContact.appKit,
            stakeStateContract=stakeStateContact,
            checkpoint=checkpoint,
            checkpointTime=checkpointTime,
            amountStaked=amountStaked,
            cycleDuration=cycleDuration,
            stakers=stakers)   

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.amountStaked,
                self.checkpoint,
                self.stakers,
                self.checkpointTime,
                self.cycleDuration
            ],ErgoValueT.LongArray)
        ]  

    @property
    def stakers(self) -> int:
        return self._stakers
    @stakers.setter
    def stakers(self, stakers: int) -> None:
        self._stakers = stakers
        self.updateRegisters()
        self.tokens[self.stakeStateContract.config.stakeTokenId] = int(1e9) - stakers

    @property
    def amountStaked(self) -> int:
        return self._amountStaked
    @amountStaked.setter
    def amountStaked(self, amountStaked: int) -> None:
        self._amountStaked = amountStaked
        self.updateRegisters()

    @property
    def checkpointTime(self) -> int:
        return self._checkpointTime
    @checkpointTime.setter
    def checkpointTime(self, checkpointTime: int) -> None:
        self._checkpointTime = checkpointTime
        self.updateRegisters()

    @property
    def cycleDuration(self) -> int:
        return self._cycleDuration
    @cycleDuration.setter
    def cycleDuration(self, cycleDuration: int) -> None:
        self._cycleDuration = cycleDuration
        self.updateRegisters()

    @property
    def checkpoint(self) -> int:
        return self._checkpoint
    @checkpoint.setter
    def checkpoint(self, checkpoint: int) -> None:
        self._checkpoint = checkpoint
        self.updateRegisters()

    @property
    def stakeStateContract(self) -> StakeStateContract:
        return self._stakeStateContract
    @stakeStateContract.setter
    def stakeStateContract(self, stakeStateContract: StakeStateContract) -> None:
        self._stakeStateContract = stakeStateContract

class StakePoolBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, stakePoolContract: StakePoolContract, emissionAmount: int, remaining: int) -> None:
        self.stakePoolContract = stakePoolContract
        tokens = {self.stakePoolContract.config.stakePoolNFT: 1, self.stakePoolContract.config.stakedTokenId: remaining}
        registers = [
            ErgoAppKit.ergoValue([
                emissionAmount
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(stakePoolContract.config.stakePoolKey, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e6),stakePoolContract.contract,tokens,registers)

        self._remaining = remaining
        self._emissionAmount = emissionAmount
        self._stakePoolKey = stakePoolContract.config.stakePoolKey

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakePoolContract: StakePoolContract):
        registers = inputBox.getRegisters()
        emissionAmount = int(registers[0].getValue().apply(0))
        remaining = int(inputBox.getTokens()[1].getValue())
        return StakePoolBox(
            appKit=stakePoolContract.appKit,
            stakePoolContract=stakePoolContract,
            emissionAmount=emissionAmount,
            remaining=remaining)   

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.emissionAmount
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(self.stakePoolKey, ErgoValueT.ByteArrayFromHex)
        ]  

    @property
    def emissionAmount(self) -> int:
        return self._emissionAmount
    @emissionAmount.setter
    def emissionAmount(self, emissionAmount: int) -> None:
        self._emissionAmount = emissionAmount
        self.updateRegisters()

    @property
    def stakePoolKey(self) -> str:
        return self._stakePoolKey
    @stakePoolKey.setter
    def stakePoolKey(self, stakePoolKey: str) -> None:
        self._stakePoolKey = stakePoolKey
        self.updateRegisters()

    @property
    def remaining(self) -> int:
        return self._remaining
    @remaining.setter
    def remaining(self, remaining: int) -> None:
        self._remaining = remaining
        self.tokens[self.stakePoolContract.config.stakedTokenId] = remaining

    @property
    def stakePoolContract(self) -> StakePoolContract:
        return self._stakePoolContract
    @stakePoolContract.setter
    def stakePoolContract(self, stakePoolContract: StakePoolContract) -> None:
        self._stakePoolContract = stakePoolContract

class StakingIncentiveBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, stakingIncentiveContract: StakingIncentiveContract, value: int) -> None:
        self.stakingIncentiveContract = stakingIncentiveContract
        self.value = value
        super().__init__(appKit,value,stakingIncentiveContract.contract)


    @staticmethod
    def fromInputBox(inputBox: InputBox, stakingIncentiveContract: StakingIncentiveContract):
        value = inputBox.getValue()
        return StakingIncentiveBox(
            appKit=stakingIncentiveContract.appKit,
            stakingIncentiveContract=stakingIncentiveContract,
            value=value)    

    @property
    def value(self) -> int:
        return self._value
    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def stakingIncentiveContract(self) -> StakingIncentiveContract:
        return self._stakingIncentiveContract
    @stakingIncentiveContract.setter
    def stakingIncentiveContract(self, stakingIncentiveContract: StakingIncentiveContract) -> None:
        self._stakingIncentiveContract = stakingIncentiveContract

class StakeProxyBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, stakeProxyContract: StakeProxyContract, amountToStake: int, userErgoTree: str, stakeTime: int) -> None:
        self.stakeProxyContract = stakeProxyContract
        tokens = {self.stakeProxyContract.config.stakedTokenId: amountToStake}
        registers = [
            ErgoAppKit.ergoValue([
                stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(11e6)+stakeProxyContract.config.proxyToStakingIncentive+stakeProxyContract.config.proxyExecutorReward+stakeProxyContract.config.proxyMinerFee,stakeProxyContract.contract,tokens,registers)

        self._amountToStake = amountToStake
        self._userErgoTree = userErgoTree
        self._stakeTime = stakeTime

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeProxyContract: StakeProxyContract):
        registers = inputBox.getRegisters()
        userErgoTree = registers[1].toHex()[4:]
        stakeTime = int(registers[0].getValue().apply(0))
        amountToStake = int(inputBox.getTokens()[0].getValue())
        return StakeProxyBox(
            appKit=stakeProxyContract.appKit,
            stakeProxyContract=stakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree=userErgoTree,
            stakeTime=stakeTime)   

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(self.userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

    @property
    def amountToStake(self) -> int:
        return self._amountToStake
    @amountToStake.setter
    def amountToStake(self, amountToStake: int) -> None:
        self._amountToStake = amountToStake
        self.tokens[self.stakeProxyContract.config.stakedTokenId] = amountToStake

    @property
    def stakeTime(self) -> int:
        return self._stakeTime
    @stakeTime.setter
    def stakeTime(self, stakeTime: int) -> None:
        self._stakeTime = stakeTime
        self.updateRegisters()

    @property
    def userErgoTree(self) -> str:
        return self._userErgoTree
    @userErgoTree.setter
    def userErgoTree(self, userErgoTree: str) -> None:
        self._userErgoTree = userErgoTree
        self.updateRegisters()

    @property
    def stakeProxyContract(self) -> StakeProxyContract:
        return self._stakeProxyContract
    @stakeProxyContract.setter
    def stakeProxyContract(self, stakeProxyContract: StakeProxyContract) -> None:
        self._stakeProxyContract = stakeProxyContract

class AddStakeProxyBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, addStakeProxyContract: AddStakeProxyContract, amountToStake: int, userErgoTree: str, stakeBox: StakeBox) -> None:
        self.addStakeProxyContract = addStakeProxyContract
        tokens = {stakeBox.stakeKey: 1, self.addStakeProxyContract.config.stakedTokenId: amountToStake}
        registers = [
            ErgoAppKit.ergoValue([
                int(0)
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e7)+addStakeProxyContract.config.proxyAddToStakingIncentive+addStakeProxyContract.config.proxyExecutorReward+addStakeProxyContract.config.proxyMinerFee,addStakeProxyContract.contract,tokens,registers)

        self._amountToStake = amountToStake
        self._userErgoTree = userErgoTree
        self._stakeBox = stakeBox

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeBox: StakeBox, addStakeProxyContract: AddStakeProxyContract):
        registers = inputBox.getRegisters()
        userErgoTree = registers[1].toHex()[4:]
        amountToStake = int(inputBox.getTokens()[1].getValue())
        return AddStakeProxyBox(
            appKit=addStakeProxyContract.appKit,
            addStakeProxyContract=addStakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree=userErgoTree,
            stakeBox=stakeBox)   

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(self.userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

    @property
    def amountToStake(self) -> int:
        return self._amountToStake
    @amountToStake.setter
    def amountToStake(self, amountToStake: int) -> None:
        self._amountToStake = amountToStake
        self.tokens[self.addStakeProxyContract.config.stakedTokenId] = amountToStake

    @property
    def stakeTime(self) -> int:
        return self._stakeTime
    @stakeTime.setter
    def stakeTime(self, stakeTime: int) -> None:
        self._stakeTime = stakeTime
        self.updateRegisters()

    @property
    def userErgoTree(self) -> str:
        return self._userErgoTree
    @userErgoTree.setter
    def userErgoTree(self, userErgoTree: str) -> None:
        self._userErgoTree = userErgoTree
        self.updateRegisters()

    @property
    def addStakeProxyContract(self) -> AddStakeProxyContract:
        return self._addStakeProxyContract
    @addStakeProxyContract.setter
    def addStakeProxyContract(self, addStakeProxyContract: AddStakeProxyContract) -> None:
        self._addStakeProxyContract = addStakeProxyContract

class UnstakeProxyBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, unstakeProxyContract: UnstakeProxyContract, amountToUnstake: int, userErgoTree: str, stakeBox: StakeBox) -> None:
        self.unstakeProxyContract = unstakeProxyContract
        tokens = {stakeBox.stakeKey: 1}
        registers = [
            ErgoAppKit.ergoValue([
                int(amountToUnstake)
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]

        super().__init__(appKit,int(1e7)+unstakeProxyContract.config.proxyToStakingIncentive+unstakeProxyContract.config.proxyExecutorReward+unstakeProxyContract.config.proxyMinerFee,unstakeProxyContract.contract,tokens,registers)

        self._amountToUnstake = amountToUnstake
        self._userErgoTree = userErgoTree
        self._stakeBox = stakeBox

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeBox: StakeBox, unstakeProxyContract: UnstakeProxyContract):
        registers = inputBox.getRegisters()
        userErgoTree = registers[1].toHex()[4:]
        amountToUnstake = int(registers[0].getValue().apply(0))
        return UnstakeProxyBox(
            appKit=unstakeProxyContract.appKit,
            unstakeProxyContract=unstakeProxyContract,
            amountToUnstake=amountToUnstake,
            userErgoTree=userErgoTree,
            stakeBox=stakeBox)   

    def updateRegisters(self):
        self.registers = [
            ErgoAppKit.ergoValue([
                self.amountToUnstake
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(self.userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

    @property
    def amountToUnstake(self) -> int:
        return self._amountToUnstake
    @amountToUnstake.setter
    def amountToUnstake(self, amountToUnstake: int) -> None:
        self._amountToUnstake = amountToUnstake
        self.updateRegisters()

    @property
    def userErgoTree(self) -> str:
        return self._userErgoTree
    @userErgoTree.setter
    def userErgoTree(self, userErgoTree: str) -> None:
        self._userErgoTree = userErgoTree
        self.updateRegisters()

    @property
    def unstakeProxyContract(self) -> UnstakeProxyContract:
        return self._unstakeProxyContract
    @unstakeProxyContract.setter
    def unstakeProxyContract(self, unstakeProxyContract: UnstakeProxyContract) -> None:
        self._unstakeProxyContract = unstakeProxyContract

class EmitTransaction(ErgoTransaction):
    def __init__(self, 
            stakeStateInput: InputBox, 
            stakePoolInput: InputBox, 
            emissionInput: InputBox,
            stakingIncentiveInput: InputBox,
            stakingConfig,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        if not stakingConfig.stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not stakingConfig.stakePoolContract.validateInputBox(stakePoolInput):
            raise InvalidInputBoxException("Stake pool input box does not match contract")
        if not stakingConfig.emissionContract.validateInputBox(emissionInput):
            raise InvalidInputBoxException("Emission input box does not match contract")
        if not stakingConfig.stakingIncentiveContract.validateInputBox(stakingIncentiveInput):
            raise InvalidInputBoxException("Emission input box does not match contract")
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakingConfig.stakeStateContract)
        stakePoolBox = StakePoolBox.fromInputBox(stakePoolInput, stakingConfig.stakePoolContract)
        emissionBox = EmissionBox.fromInputBox(emissionInput, stakingConfig.emissionContract)
        stakingIncentiveBox = StakingIncentiveBox.fromInputBox(stakingIncentiveInput, stakingConfig.stakingIncentiveContract)
        if stakeStateBox.checkpointTime + stakeStateBox.cycleDuration > self.preHeader.getTimestamp():
            raise InvalidTransactionConditionsException("Emission time not reached yet")
        if emissionBox.stakers > 0:
            raise InvalidTransactionConditionsException("Previous emission not finished yet")
        dust = emissionBox.emissionRemaining
        stakePoolBox.remaining = stakePoolBox.remaining - stakePoolBox.emissionAmount + dust
        emissionBox.emissionRemaining = stakePoolBox.emissionAmount
        emissionBox.checkpoint = stakeStateBox.checkpoint
        emissionBox.amountStaked = stakeStateBox.amountStaked
        emissionBox.stakers = stakeStateBox.stakers
        emissionBox.emissionAmount = stakePoolBox.emissionAmount
        stakeStateBox.amountStaked = stakeStateBox.amountStaked + stakePoolBox.emissionAmount - dust
        stakeStateBox.checkpoint = stakeStateBox.checkpoint + 1
        stakeStateBox.checkpointTime = stakeStateBox.checkpointTime + stakeStateBox.cycleDuration
        stakingIncentiveBox.value -= (stakingConfig.emitMinerFee + stakingConfig.emitReward)
        txExecutorBox = ErgoBox(stakingConfig.appKit,stakingConfig.emitReward,stakingConfig.appKit.contractFromAddress(address))
        self.inputs = [stakeStateInput,stakePoolInput,emissionInput,stakingIncentiveInput]
        self.outputs = [stakeStateBox.outBox,stakePoolBox.outBox,emissionBox.outBox,stakingIncentiveBox.outBox,txExecutorBox.outBox]
        self.fee = stakingConfig.emitMinerFee
        self.changeAddress = address

class CompoundTransaction(ErgoTransaction):
    def __init__(self,  
            emissionInput: InputBox,
            stakeInputs: List[InputBox],
            stakingIncentiveInput: InputBox,
            stakingConfig,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        if not stakingConfig.emissionContract.validateInputBox(emissionInput):
            raise InvalidInputBoxException("Emission input box does not match contract")
        for stakeInput in stakeInputs:
            if not stakingConfig.stakeContract.validateInputBox(stakeInput):
                raise InvalidInputBoxException("Stake input box does not match contract")
        emissionBox = EmissionBox.fromInputBox(emissionInput, stakingConfig.emissionContract)
        stakingIncentiveBox = StakingIncentiveBox.fromInputBox(stakingIncentiveInput, stakingConfig.stakingIncentiveContract)
        stakeBoxes = []
        stakeRewards = 0
        for stakeInput in stakeInputs:
            box = StakeBox.fromInputBox(stakeInput,stakingConfig.stakeContract)
            if box.checkpoint != emissionBox.checkpoint:
                raise InvalidTransactionConditionsException("Stake box not on same checkpoint as emission box")
            box.checkpoint = box.checkpoint + 1
            reward = int(box.amountStaked * emissionBox.emissionAmount / emissionBox.amountStaked)
            stakeRewards += reward
            box.amountStaked += reward
            stakeBoxes.append(box.outBox)

        emissionBox.emissionRemaining -= stakeRewards
        emissionBox.stakers -= len(stakeBoxes)
        reward = int(stakingConfig.baseCompoundReward + stakingConfig.variableCompoundReward * len(stakeBoxes))
        minerFee = int(stakingConfig.baseCompoundMinerFee + stakingConfig.variableCompoundMinerFee * len(stakeBoxes))
        stakingIncentiveBox.value -= (reward + minerFee)
        txExecutorBox = ErgoBox(stakingConfig.appKit,reward,stakingConfig.appKit.contractFromAddress(address))
        self.inputs = [emissionInput] + stakeInputs + [stakingIncentiveInput]
        self.outputs = [emissionBox.outBox] + stakeBoxes + [stakingIncentiveBox.outBox, txExecutorBox.outBox]
        self.fee = minerFee
        self.changeAddress = address

class StakeTransaction(ErgoTransaction):
    def __init__(self, 
            stakeStateInput: InputBox,
            stakeProxyInput: InputBox,
            stakingConfig,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        if not stakingConfig.stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not stakingConfig.stakeProxyContract.validateInputBox(stakeProxyInput):
            raise InvalidInputBoxException("Stake proxy input box does not match contract")
        stakeProxyBox = StakeProxyBox.fromInputBox(stakeProxyInput, stakingConfig.stakeProxyContract)
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakingConfig.stakeStateContract)
        stakeStateBox.amountStaked += stakeProxyBox.amountToStake
        stakeStateBox.stakers += 1

        userOutput = stakingConfig.appKit.mintToken(
            value=int(1e7),
            tokenId=stakeStateInput.getId().toString(),
            tokenName=f'{stakingConfig.stakedTokenName} Stake Key',
            tokenDesc=f'{{"originalAmountStaked": {stakeProxyBox.amountToStake*10**(-1*stakingConfig.stakedTokenDecimals)}, "stakeTime": "{datetime.fromtimestamp(stakeProxyBox.stakeTime/1000)}"}}',
            mintAmount=1,
            decimals=0,
            contract=stakingConfig.appKit.contractFromTree(stakingConfig.appKit.treeFromBytes(bytes.fromhex(stakeProxyBox.userErgoTree)))
        )

        stakeBox = StakeBox(
            appKit=stakingConfig.appKit,
            stakeContract=stakingConfig.stakeContract,
            checkpoint=stakeStateBox.checkpoint,
            stakeTime=stakeProxyBox.stakeTime,
            amountStaked=stakeProxyBox.amountToStake,
            stakeKey=stakeStateInput.getId().toString()
        )

        stakingIncentiveBox = StakingIncentiveBox(stakingConfig.appKit, stakingConfig.stakingIncentiveContract, stakingConfig.proxyToStakingIncentive)

        txExecutorBox = ErgoBox(stakingConfig.appKit,stakingConfig.proxyExecutorReward,stakingConfig.appKit.contractFromAddress(address))

        self.inputs = [stakeStateInput, stakeProxyInput]
        self.outputs = [stakeStateBox.outBox, stakeBox.outBox, userOutput, stakingIncentiveBox.outBox, txExecutorBox.outBox]
        self.fee = stakingConfig.proxyMinerFee
        self.changeAddress = address

class AddStakeTransaction(ErgoTransaction):
    def __init__(self, 
            stakeStateInput: InputBox,
            stakeInput: InputBox,
            addStakeProxyInput: InputBox,
            stakingConfig,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        if not stakingConfig.stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not stakingConfig.stakeContract.validateInputBox(stakeInput):
            raise InvalidInputBoxException("Stake input box does not match contract")
        if not stakingConfig.addStakeProxyContract.validateInputBox(addStakeProxyInput):
            raise InvalidInputBoxException("Add Stake Proxy input box does not match contract")
        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)
        addStakeProxyBox = AddStakeProxyBox.fromInputBox(addStakeProxyInput, stakeBox, stakingConfig.addStakeProxyContract)
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakingConfig.stakeStateContract)
        stakeStateBox.amountStaked += addStakeProxyBox.amountToStake

        stakeBox.amountStaked += addStakeProxyBox.amountToStake

        userOutput = ErgoBox(
            appKit=stakingConfig.appKit,
            value=int(1e7),
            contract=stakingConfig.appKit.contractFromTree(stakingConfig.appKit.treeFromBytes(bytes.fromhex(addStakeProxyBox.userErgoTree))),
            tokens={stakeBox.stakeKey: 1}
        )

        stakingIncentiveBox = StakingIncentiveBox(stakingConfig.appKit, stakingConfig.stakingIncentiveContract, stakingConfig.proxyAddToStakingIncentive)

        txExecutorBox = ErgoBox(stakingConfig.appKit,stakingConfig.proxyExecutorReward,stakingConfig.appKit.contractFromAddress(address))

        self.inputs = [stakeStateInput, stakeInput, addStakeProxyInput]
        self.outputs = [stakeStateBox.outBox, stakeBox.outBox, userOutput.outBox, stakingIncentiveBox.outBox, txExecutorBox.outBox]
        self.fee = stakingConfig.proxyMinerFee
        self.changeAddress = address

class UnstakeTransaction(ErgoTransaction):
    def __init__(self, 
            stakeStateInput: InputBox,
            stakeInput: InputBox,
            unstakeProxyInput: InputBox,
            stakingConfig,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        if not stakingConfig.stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not stakingConfig.stakeContract.validateInputBox(stakeInput):
            raise InvalidInputBoxException("Stake input box does not match contract")
        if not stakingConfig.unstakeProxyContract.validateInputBox(unstakeProxyInput):
            raise InvalidInputBoxException("Unstake proxy input box does not match contract")

        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)
        unstakeProxyBox = UnstakeProxyBox.fromInputBox(unstakeProxyInput, stakeBox, stakingConfig.unstakeProxyContract)
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakingConfig.stakeStateContract)
        stakeStateBox.amountStaked -= unstakeProxyBox.amountToUnstake
        userTokens = {stakingConfig.stakedTokenId: unstakeProxyBox.amountToUnstake}
        if stakeBox.amountStaked <= unstakeProxyBox.amountToUnstake:
            stakeStateBox.stakers -= 1
            self.tokensToBurn = {stakeBox.stakeKey: 1}
        else:
            userTokens[stakeBox.stakeKey] = 1

        stakeBox.amountStaked -= unstakeProxyBox.amountToUnstake

        userOutput = ErgoBox(
            appKit=stakingConfig.appKit,
            value=int(1e7),
            contract=stakingConfig.appKit.contractFromTree(stakingConfig.appKit.treeFromBytes(bytes.fromhex(unstakeProxyBox.userErgoTree))),
            tokens=userTokens
        )

        stakingIncentiveBox = StakingIncentiveBox(stakingConfig.appKit, stakingConfig.stakingIncentiveContract, int(1e8))

        txExecutorBox = ErgoBox(stakingConfig.appKit,int(2e6),stakingConfig.appKit.contractFromAddress(address))

        self.inputs = [stakeStateInput, stakeInput, unstakeProxyInput]

        if stakeBox.amountStaked <= 0:
            self.outputs = [stakeStateBox.outBox, userOutput.outBox, stakingIncentiveBox.outBox, txExecutorBox.outBox]
        else:
            self.outputs = [stakeStateBox.outBox, userOutput.outBox, stakeBox.outBox, stakingIncentiveBox.outBox, txExecutorBox.outBox]
        self.fee = int(2e6)
        self.changeAddress = address

@dataclass
class StakingConfig:
    appKit: ErgoAppKit
    stakeStateNFT: str
    stakePoolNFT: str
    emissionNFT: str
    stakeTokenId: str
    stakedTokenId: str
    stakePoolKey: str
    stakedTokenName: str
    stakedTokenDecimals: int
    proxyToStakingIncentive: int
    proxyAddToStakingIncentive: int
    proxyExecutorReward: int
    proxyMinerFee: int
    dustCollectionReward: int
    dustCollectionMinerFee: int
    emitReward: int
    emitMinerFee: int
    baseCompoundReward: int
    baseCompoundMinerFee: int
    variableCompoundReward: int
    variableCompoundMinerFee: int
    stakeStateContract: StakeStateContract = None
    stakePoolContract: StakePoolContract = None
    emissionContract: EmissionContract = None
    stakeContract: StakeContract = None
    stakeProxyContract: StakeProxyContract = None
    addStakeProxyContract: AddStakeProxyContract = None
    unstakeProxyContract: UnstakeProxyContract = None
    stakingIncentiveContract: StakingIncentiveContract = None

def PaideiaTestConfig(appKit: ErgoAppKit) -> StakingConfig:
    result = StakingConfig(
    appKit = appKit,
    stakeStateNFT = "efdcb8ec05cf4da345530293860fa4b7106575fd6c2acc91a4e951e8b195c01f",
    stakePoolNFT = "56aa0514bae0abaa32f93af1c5f50e41fb0146abc8aeef6c6f710bc3c9986b58",
    emissionNFT = "8b9afefb32e2a6ad9c622d49826afb458c3f329a433a1bf928208f25f43fb734",
    stakeTokenId = "91e6e1e2e9a35a16848c66d58ac100be0112024016922e4783825183396efe0a",
    stakedTokenId = "c9cce92efe5beb4253456b0ccf3bb97ce5ddcf69fb382c2a00722f33bd97eb46",
    stakePoolKey= "6605390819ab84f716d808874ac1f48ea9cc43526a81262210ffb6177eb2ce63",
    stakedTokenName = "Paideia Test",
    stakedTokenDecimals = 4,
    proxyToStakingIncentive = int(1e8),
    proxyAddToStakingIncentive = int(1e7),
    proxyExecutorReward = int(2e6),
    proxyMinerFee = int(2e6),
    dustCollectionReward = int(5e5),
    dustCollectionMinerFee = int(1e6),
    emitReward = int(3e6),
    emitMinerFee = int(1e6),
    baseCompoundReward = int(5e5),
    baseCompoundMinerFee = int(1e6),
    variableCompoundReward = int(15e4),
    variableCompoundMinerFee = int(1e5))
    result.stakeContract = StakeContract(result)
    result.stakeStateContract = StakeStateContract(result)
    result.stakePoolContract = StakePoolContract(result)
    result.emissionContract = EmissionContract(result)
    result.stakingIncentiveContract = StakingIncentiveContract(result)
    result.stakeProxyContract = StakeProxyContract(result)
    result.addStakeProxyContract = AddStakeProxyContract(result)
    result.unstakeProxyContract = UnstakeProxyContract(result)
    return result
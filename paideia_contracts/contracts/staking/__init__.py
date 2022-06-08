from dataclasses import dataclass
from datetime import datetime
from hashlib import blake2b
import os
from time import time
from typing import Dict, List
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT
from ergo_python_appkit.ErgoBox import ErgoBox
from ergo_python_appkit.ErgoContractBase import ErgoContractBase
import requests

from org.ergoplatform.appkit import ErgoValue, InputBox
from sigmastate.Values import ErgoTree

from ergo_python_appkit.ErgoTransaction import ErgoTransaction

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
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakingConfig.stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionFeeAddress": ErgoAppKit.ergoValue("0008cd02189359b825e96aa3c7af90c9958d85daf8f86358382db3306e024c5aeea1e8ec", ErgoValueT.ByteArrayFromHex).getValue()
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
        if emissionRemaining > 0:
            self.tokens[self.emissionContract.config.stakedTokenId] = emissionRemaining
        else:
            self.tokens.pop(self.emissionContract.config.stakedTokenId, None)

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
        if amountStaked < 1000:
            raise InvalidInputBoxException("Stake box needs more than 1000 tokens")
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
        tokens = {self.stakeStateContract.config.stakeStateNFT: 1, self.stakeStateContract.config.stakeTokenId: int(1e12)-stakers}
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
        self.tokens[self.stakeStateContract.config.stakeTokenId] = int(1e12) - stakers

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

        valueAdjustment = int(0) if stakeBox.amountStaked > amountToUnstake else int(1e6)

        super().__init__(appKit,int(1e7)+unstakeProxyContract.config.proxyToStakingIncentive+unstakeProxyContract.config.proxyExecutorReward+unstakeProxyContract.config.proxyMinerFee-valueAdjustment,unstakeProxyContract.contract,tokens,registers)

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
        emissionBox.emissionRemaining = stakePoolBox.emissionAmount - int(stakePoolBox.emissionAmount/100)
        emissionBox.checkpoint = stakeStateBox.checkpoint
        emissionBox.amountStaked = stakeStateBox.amountStaked
        emissionBox.stakers = stakeStateBox.stakers
        emissionBox.emissionAmount = stakePoolBox.emissionAmount - int(stakePoolBox.emissionAmount/100)
        stakeStateBox.amountStaked = stakeStateBox.amountStaked + (stakePoolBox.emissionAmount - int(stakePoolBox.emissionAmount/100)) - dust
        stakeStateBox.checkpoint = stakeStateBox.checkpoint + 1
        stakeStateBox.checkpointTime = stakeStateBox.checkpointTime + stakeStateBox.cycleDuration
        emissionFeeBox = ErgoBox(
            stakingConfig.appKit,
            int(1e6),
            stakingConfig.appKit.contractFromAddress("9ehtGMAL6gxjjz7TY8QdKnbsXzt8XSgEX4MuMKauf8cZpPumEtU"),
            tokens={stakingConfig.stakedTokenId: int(stakePoolBox.emissionAmount/100)}
        )
        stakingIncentiveBox.value -= (stakingConfig.emitMinerFee + stakingConfig.emitReward + int(1e6))
        txExecutorBox = ErgoBox(stakingConfig.appKit,stakingConfig.emitReward,stakingConfig.appKit.contractFromAddress(address))
        self.inputs = [stakeStateInput,stakePoolInput,emissionInput,stakingIncentiveInput]
        self.outputs = [stakeStateBox.outBox,stakePoolBox.outBox,emissionBox.outBox,emissionFeeBox.outBox,stakingIncentiveBox.outBox,txExecutorBox.outBox]
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

class CreateStakeProxyTransaction(ErgoTransaction):
    def __init__(self, 
            userInputs: List[InputBox],
            stakingConfig,
            amountToStake: int,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)
        
        stakeProxyBox = StakeProxyBox(
            appKit=stakingConfig.appKit,
            stakeProxyContract=stakingConfig.stakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree=stakingConfig.appKit.contractFromAddress(address).getErgoTree().bytesHex(),
            stakeTime=int(time()*1000)
        )

        if not ErgoAppKit.boxesCovered(userInputs, stakeProxyBox.value + int(1e6), stakeProxyBox.tokens):
            raise InvalidTransactionConditionsException("Not enough erg/tokens in the user input boxes")

        self.inputs = userInputs
        self.outputs = [stakeProxyBox.outBox]
        self.fee = int(1e6)
        self.changeAddress = address

    @staticmethod
    def assetsRequired(stakingConfig, amountToStake: int) -> AssetsRequired:
        stakeProxyBox = StakeProxyBox(
            appKit=stakingConfig.appKit,
            stakeProxyContract=stakingConfig.stakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree="",
            stakeTime=int(time()*1000)
        )
        return AssetsRequired(
            nErgRequired=int(1e6) + stakeProxyBox.value,
            tokensRequired=stakeProxyBox.tokens
        )

class CreateAddStakeProxyTransaction(ErgoTransaction):
    def __init__(self, 
            userInputs: List[InputBox],
            stakeInput: InputBox,
            stakingConfig,
            amountToStake: int,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)

        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)
        
        addStakeProxyBox = AddStakeProxyBox(
            appKit=stakingConfig.appKit,
            addStakeProxyContract=stakingConfig.addStakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree=stakingConfig.appKit.contractFromAddress(address).getErgoTree().bytesHex(),
            stakeBox=stakeBox
        )

        if not ErgoAppKit.boxesCovered(userInputs, addStakeProxyBox.value + int(1e6), addStakeProxyBox.tokens):
            raise InvalidTransactionConditionsException("Not enough erg/tokens in the user input boxes")

        self.inputs = userInputs
        self.outputs = [addStakeProxyBox.outBox]
        self.fee = int(1e6)
        self.changeAddress = address

    @staticmethod
    def assetsRequired(stakingConfig, amountToStake: int, stakeInput: InputBox) -> AssetsRequired:
        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)
        addStakeProxyBox = AddStakeProxyBox(
            appKit=stakingConfig.appKit,
            addStakeProxyContract=stakingConfig.addStakeProxyContract,
            amountToStake=amountToStake,
            userErgoTree="",
            stakeBox=stakeBox
        )
        return AssetsRequired(
            nErgRequired=int(1e6) + addStakeProxyBox.value,
            tokensRequired=addStakeProxyBox.tokens
        )

class CreateUnstakeProxyTransaction(ErgoTransaction):
    def __init__(self, 
            userInputs: List[InputBox],
            stakeInput: InputBox,
            stakingConfig,
            amountToUnstake: int,
            address: str) -> None:
        super().__init__(stakingConfig.appKit)

        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)

        unstakeProxyBox = UnstakeProxyBox(
            appKit=stakingConfig.appKit,
            unstakeProxyContract=stakingConfig.unstakeProxyContract,
            amountToUnstake=min(amountToUnstake,stakeBox.amountStaked),
            userErgoTree=stakingConfig.appKit.contractFromAddress(address).getErgoTree().bytesHex(),
            stakeBox=stakeBox
        )

        if not ErgoAppKit.boxesCovered(userInputs, unstakeProxyBox.value + int(1e6), unstakeProxyBox.tokens):
            raise InvalidTransactionConditionsException("Not enough erg/tokens in the user input boxes")

        self.inputs = userInputs
        self.outputs = [unstakeProxyBox.outBox]
        self.fee = int(1e6)
        self.changeAddress = address

    @staticmethod
    def assetsRequired(stakingConfig, amountToUnstake: int, stakeInput: InputBox) -> AssetsRequired:
        stakeBox = StakeBox.fromInputBox(stakeInput, stakingConfig.stakeContract)
        unstakeProxyBox = UnstakeProxyBox(
            appKit=stakingConfig.appKit,
            unstakeProxyContract=stakingConfig.unstakeProxyContract,
            amountToUnstake=amountToUnstake,
            userErgoTree="",
            stakeBox=stakeBox
        )
        return AssetsRequired(
            nErgRequired=int(1e6) + unstakeProxyBox.value,
            tokensRequired=unstakeProxyBox.tokens
        )

class ConsolidateDustTransaction(ErgoTransaction):
    def __init__(self, 
        incentiveDustInputs: List[InputBox],
        stakingConfig,
        address: str) -> None:
        super().__init__(stakingConfig.appKit)

        for idi in incentiveDustInputs:
            if not stakingConfig.stakingIncentiveContract.validateInputBox(idi):
                raise InvalidInputBoxException("Not a valid staking incentive box")
            if idi.getValue() > int(1e7):
                raise InvalidInputBoxException("Too much erg in box")
        
        dustCollected = 99999999999999999999999
        done = False
        while not done:
            currentDustCollected = -1 * stakingConfig.dustCollectionMinerFee
            filteredIncentiveDustInputs = []
            done = True
            for idi in incentiveDustInputs:
                if idi.getValue() < dustCollected:
                    currentDustCollected += idi.getValue() - stakingConfig.dustCollectionReward
                    filteredIncentiveDustInputs.append(idi)
                else:
                    done = False
            incentiveDustInputs = filteredIncentiveDustInputs
            if dustCollected != currentDustCollected:
                done = False
            dustCollected = currentDustCollected

        if len(incentiveDustInputs) < 2:
            raise InvalidTransactionConditionsException("Not enough dust")

        incentiveOutput = StakingIncentiveBox(
            appKit=stakingConfig.appKit,
            stakingIncentiveContract=stakingConfig.stakingIncentiveContract,
            value=dustCollected
        )

        txExecutorBox = ErgoBox(stakingConfig.appKit,stakingConfig.dustCollectionReward*len(incentiveDustInputs),stakingConfig.appKit.contractFromAddress(address))

        self.inputs = incentiveDustInputs
        self.outputs = [incentiveOutput.outBox,txExecutorBox.outBox]
        self.fee = stakingConfig.dustCollectionMinerFee
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

def PaideiaConfig(appKit: ErgoAppKit) -> StakingConfig:
    result = StakingConfig(
        appKit = appKit,
        stakeStateNFT = "b682ad9e8c56c5a0ba7fe2d3d9b2fbd40af989e8870628f4a03ae1022d36f091",
        stakePoolNFT = "93cda90b4fe24f075d7961fa0d1d662fdc7e1349d313059b9618eecb16c5eade",
        emissionNFT = "12bbef36eaa5e61b64d519196a1e8ebea360f18aba9b02d2a21b16f26208960f",
        stakeTokenId = "245957934c20285ada547aa8f2c8e6f7637be86a1985b3e4c36e4e1ad8ce97ab",
        stakedTokenId = "1fd6e032e8476c4aa54c18c1a308dce83940e8f4a28f576440513ed7326ad489",
        stakePoolKey = "b311425409ff2e8f5901d230788c6628b5846be0b9c66621e4880b086dd5eaef",
        stakedTokenName = "Paideia",
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

def PaideiaTestConfig(appKit: ErgoAppKit) -> StakingConfig:
    result = StakingConfig(
        appKit = appKit,
        stakeStateNFT = "aad0b57e456c696841155d414184442ff269f233a3ac87f52050003c1bdce2cd",
        stakePoolNFT = "cefbfdad99eb0a3bf836d561d3c844df4d3a9d1e7a7c8479a9262165ce787b81",
        emissionNFT = "2ac6583dcbc11e13758ca846388dadb67d5f09fee27243c0f42fd280c625b347",
        stakeTokenId = "c1eafc184b24ac1fb59d238f659cd6bdcc258604fa29c078a6667808dad94889",
        stakedTokenId = "001475b06ed4d2a2fe1e244c951b4c70d924b933b9ee05227f2f2da7d6f46fd3",
        stakePoolKey = "c50a7127b95f9ca0dd2f8da8ed6c1c93d5a791c899103f88baa8127c9ab8783b",
        stakedTokenName = "PaideiaTest",
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

def BootstrapStaking(appKit: ErgoAppKit, nodeAddress: str, tokenId: str, stakingStart: int, stakingCycleDuration: int, dailyEmission: int, stakePoolSize: int) -> StakingConfig:
    res = requests.get(f"https://api.ergoplatform.com/api/v1/tokens/{tokenId}")
    stakedTokenName = res.json()["name"]
    stakedTokenDecimals = res.json()["decimals"]
    print(stakedTokenName)
    nodeContract = appKit.contractFromAddress(nodeAddress)
    nodeInputs = appKit.boxesToSpend(nodeAddress,int(14e6),{tokenId: int(stakePoolSize*10**stakedTokenDecimals)})

    #Stake state nft mint
    stakeStateNFT = nodeInputs[0].getId().toString()
    stakeStateNFTBox = appKit.mintToken(
        value=int(1e6),
        tokenId=stakeStateNFT,
        tokenName=f"{stakedTokenName} Stake State NFT",
        tokenDesc=f"Stake State NFT for {stakedTokenName} staking setup",
        mintAmount=1,
        decimals=0,
        contract=nodeContract
    )
    nodeBox = ErgoBox(appKit,int(12e6),contract=nodeContract,tokens={tokenId: int(stakePoolSize*10**stakedTokenDecimals)})
    stakeStateMintunsignedTx = ErgoTransaction(appKit)
    stakeStateMintunsignedTx.inputs=nodeInputs
    stakeStateMintunsignedTx.outputs=[stakeStateNFTBox,nodeBox.outBox]
    stakeStateMintunsignedTx.fee=int(1e6)
    stakeStateMintunsignedTx.changeAddress=nodeAddress
    stakeStateMintTx = appKit.signTransactionWithNode(stakeStateMintunsignedTx.unsignedTx)
    appKit.sendTransaction(stakeStateMintTx)

    #Stake Pool NFT mint
    nodeInputs = stakeStateMintTx.getOutputsToSpend()
    stakePoolNFT = nodeInputs[1].getId().toString()
    stakePoolNFTBox = appKit.mintToken(
        value=int(1e6),
        tokenId=stakePoolNFT,
        tokenName=f"{stakedTokenName} Stake Pool NFT",
        tokenDesc=f"Stake Pool NFT for {stakedTokenName} staking setup",
        mintAmount=1,
        decimals=0,
        contract=nodeContract
    )
    nodeBox = ErgoBox(appKit,nodeInputs[1].getValue()-int(2e6),contract=nodeContract,tokens={tokenId: int(stakePoolSize*10**stakedTokenDecimals)})
    stakePoolMintunsignedTx = ErgoTransaction(appKit)
    stakePoolMintunsignedTx.inputs=[nodeInputs[1]]
    stakePoolMintunsignedTx.outputs=[stakePoolNFTBox,nodeBox.outBox]
    stakePoolMintunsignedTx.fee=int(1e6)
    stakePoolMintunsignedTx.changeAddress=nodeAddress
    stakePoolMintTx = appKit.signTransactionWithNode(stakePoolMintunsignedTx.unsignedTx)
    appKit.sendTransaction(stakePoolMintTx)

    #Emission NFT mint
    nodeInputs = stakePoolMintTx.getOutputsToSpend()
    emissionNFT = nodeInputs[1].getId().toString()
    emissionNFTBox = appKit.mintToken(
        value=int(1e6),
        tokenId=emissionNFT,
        tokenName=f"{stakedTokenName} Emission NFT",
        tokenDesc=f"Emission NFT for {stakedTokenName} staking setup",
        mintAmount=1,
        decimals=0,
        contract=nodeContract
    )
    nodeBox = ErgoBox(appKit,nodeInputs[1].getValue()-int(2e6),contract=nodeContract,tokens={tokenId: int(stakePoolSize*10**stakedTokenDecimals)})
    emissionMintunsignedTx = ErgoTransaction(appKit)
    emissionMintunsignedTx.inputs=[nodeInputs[1]]
    emissionMintunsignedTx.outputs=[emissionNFTBox,nodeBox.outBox]
    emissionMintunsignedTx.fee=int(1e6)
    emissionMintunsignedTx.changeAddress=nodeAddress
    emissionMintTx = appKit.signTransactionWithNode(emissionMintunsignedTx.unsignedTx)
    appKit.sendTransaction(emissionMintTx)


    #Stake token mint
    nodeInputs = emissionMintTx.getOutputsToSpend()
    stakeTokenId = nodeInputs[1].getId().toString()
    stakeTokenBox = appKit.mintToken(
        value=int(1e6),
        tokenId=stakeTokenId,
        tokenName=f"{stakedTokenName} Stake Token",
        tokenDesc=f"Stake Token for {stakedTokenName} staking setup",
        mintAmount=int(1e12),
        decimals=0,
        contract=nodeContract
    )
    nodeBox = ErgoBox(appKit,nodeInputs[1].getValue()-int(2e6),contract=nodeContract,tokens={tokenId: int(stakePoolSize*10**stakedTokenDecimals)})
    stakeTokenMintunsignedTx = ErgoTransaction(appKit)
    stakeTokenMintunsignedTx.inputs=[nodeInputs[1]]
    stakeTokenMintunsignedTx.outputs=[stakeTokenBox,nodeBox.outBox]
    stakeTokenMintunsignedTx.fee=int(1e6)
    stakeTokenMintunsignedTx.changeAddress=nodeAddress
    stakeTokenMintTx = appKit.signTransactionWithNode(stakeTokenMintunsignedTx.unsignedTx)
    appKit.sendTransaction(stakeTokenMintTx)


    #Stake pool key mint
    nodeInputs = stakeTokenMintTx.getOutputsToSpend()
    stakePoolKey = nodeInputs[1].getId().toString()
    stakePoolKeyBox = appKit.mintToken(
        value=int(1e6),
        tokenId=stakePoolKey,
        tokenName=f"{stakedTokenName} Stake Pool Key",
        tokenDesc=f"Stake Pool Key for {stakedTokenName} staking setup",
        mintAmount=2,
        decimals=0,
        contract=nodeContract
    )
    nodeBox = ErgoBox(appKit,nodeInputs[1].getValue()-int(2e6),contract=nodeContract,tokens={tokenId: int(stakePoolSize*10**stakedTokenDecimals)})
    stakePoolKeyMintunsignedTx = ErgoTransaction(appKit)
    stakePoolKeyMintunsignedTx.inputs=[nodeInputs[1]]
    stakePoolKeyMintunsignedTx.outputs=[stakePoolKeyBox,nodeBox.outBox]
    stakePoolKeyMintunsignedTx.fee=int(1e6)
    stakePoolKeyMintunsignedTx.changeAddress=nodeAddress
    stakePoolKeyMintTx = appKit.signTransactionWithNode(stakePoolKeyMintunsignedTx.unsignedTx)
    appKit.sendTransaction(stakePoolKeyMintTx)


    config = StakingConfig(
    appKit = appKit,
    stakeStateNFT = stakeStateNFT,
    stakePoolNFT = stakePoolNFT,
    emissionNFT = emissionNFT,
    stakeTokenId = stakeTokenId,
    stakedTokenId = tokenId,
    stakePoolKey = stakePoolKey,
    stakedTokenName = stakedTokenName,
    stakedTokenDecimals = stakedTokenDecimals,
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
    config.stakeContract = StakeContract(config)
    config.stakeStateContract = StakeStateContract(config)
    config.stakePoolContract = StakePoolContract(config)
    config.emissionContract = EmissionContract(config)
    config.stakingIncentiveContract = StakingIncentiveContract(config)
    config.stakeProxyContract = StakeProxyContract(config)
    config.addStakeProxyContract = AddStakeProxyContract(config)
    config.unstakeProxyContract = UnstakeProxyContract(config)
    
    stakeStateBox = StakeStateBox(
        appKit=appKit,
        stakeStateContract=config.stakeStateContract,
        checkpoint=0,
        checkpointTime=stakingStart-stakingCycleDuration,
        amountStaked=0,
        cycleDuration=stakingCycleDuration,
        stakers=0
        )

    stakePoolBox = StakePoolBox(
        appKit=appKit,
        stakePoolContract=config.stakePoolContract,
        emissionAmount=int(dailyEmission*10**stakedTokenDecimals),
        remaining=int(stakePoolSize*10**stakedTokenDecimals)
    )

    emissionBox = EmissionBox(
        appKit=appKit,
        emissionContract=config.emissionContract,
        emissionRemaining=0,
        amountStaked=0,
        checkpoint=-1,
        stakers=0,
        emissionAmount=int(dailyEmission*10**stakedTokenDecimals)
    )

    bootstrapUnsignedTx = ErgoTransaction(appKit)
    bootstrapUnsignedTx.inputs = [stakeStateMintTx.getOutputsToSpend()[0],stakePoolMintTx.getOutputsToSpend()[0],stakeTokenMintTx.getOutputsToSpend()[0],emissionMintTx.getOutputsToSpend()[0],stakePoolKeyMintTx.getOutputsToSpend()[1]]
    bootstrapUnsignedTx.outputs = [stakeStateBox.outBox,stakePoolBox.outBox,emissionBox.outBox]
    bootstrapUnsignedTx.fee = int(1e6)
    bootstrapUnsignedTx.changeAddress = nodeAddress
    bootstrapTx = appKit.signTransactionWithNode(bootstrapUnsignedTx.unsignedTx)
    appKit.sendTransaction(bootstrapTx)

    return config
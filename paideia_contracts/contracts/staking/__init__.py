from datetime import datetime
from hashlib import blake2b
import os
from time import time
from typing import List
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT
from paideia_contracts.contracts.ErgoBox import ErgoBox
from paideia_contracts.contracts.ErgoContractBase import ErgoContractBase

from org.ergoplatform.appkit import InputBox
from sigmastate.Values import ErgoTree

from paideia_contracts.contracts.ErgoTransaction import ErgoTransaction

class InvalidInputBoxException(Exception): pass
class InvalidTransactionConditionsException(Exception): pass

class StakeContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakeTokenID: str, stakedTokenID: str, emissionNFT: str) -> None:
        self.nft = stakeTokenID
        self.stakedTokenId = stakedTokenID
        self.stakeStateNFT = stakeStateNFT
        self.emissionNFT = emissionNFT
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(emissionNFT, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stake.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.nft:
            return False
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        if len(registers[0].getValue()) != 2:
            return False
        return super().validateInputBox(inBox)

    @property
    def nft(self) -> str:
        return self._nft
    @nft.setter
    def nft(self, nft: str) -> None:
        self._nft = nft

    @property
    def stakedTokenId(self) -> str:
        return self._stakedTokenId
    @stakedTokenId.setter
    def stakedTokenId(self, stakedTokenId: str) -> None:
        self._stakedTokenId = stakedTokenId

    @property
    def stakeStateNFT(self) -> str:
        return self._stakeStateNFT
    @stakeStateNFT.setter
    def stakeStateNFT(self, stakeStateNFT: str) -> None:
        self._stakeStateNFT = stakeStateNFT

    @property
    def emissionNFT(self) -> str:
        return self._emissionNFT
    @emissionNFT.setter
    def emissionNFT(self, emissionNFT: str) -> None:
        self._emissionNFT = emissionNFT

class StakeStateContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakeTokenID: str, stakedTokenID: str, emissionNFT: str, stakePoolNFT: str, stakeErgoTree: ErgoTree) -> None:
        self.nft = stakeStateNFT
        self.stakedTokenId = stakedTokenID
        self.stakePoolNFT = stakePoolNFT
        self.stakeTokenId = stakeTokenID
        self.emissionNFT = emissionNFT
        mapping = {
            "_stakedTokenID": ErgoAppKit.ergoValue(stakedTokenID, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakePoolNFT": ErgoAppKit.ergoValue(stakePoolNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(emissionNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeContractHash": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakeErgoTree.bytesHex())).digest(), ErgoValueT.ByteArray).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakeState.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.nft:
            return False
        registers = inBox.getRegisters()
        if len(registers) > 1:
            return False
        if len(registers[0].getValue()) != 5:
            return False
        return super().validateInputBox(inBox)

    @staticmethod
    def FromStakeContract(stakeContract: StakeContract, stakePoolNFT: str):
        return StakeStateContract(stakeContract.appKit,stakeContract.stakeStateNFT,stakeContract.nft,stakeContract.stakedTokenId,stakeContract.emissionNFT,stakePoolNFT,stakeContract.contract.getErgoTree())

    @property
    def nft(self) -> str:
        return self._nft
    @nft.setter
    def nft(self, nft: str) -> None:
        self._nft = nft

    @property
    def stakedTokenId(self) -> str:
        return self._stakedTokenId
    @stakedTokenId.setter
    def stakedTokenId(self, stakedTokenId: str) -> None:
        self._stakedTokenId = stakedTokenId

    @property
    def stakePoolNFT(self) -> str:
        return self._stakePoolNFT
    @stakePoolNFT.setter
    def stakePoolNFT(self, stakePoolNFT: str) -> None:
        self._stakePoolNFT = stakePoolNFT

    @property
    def emissionNFT(self) -> str:
        return self._emissionNFT
    @emissionNFT.setter
    def emissionNFT(self, emissionNFT: str) -> None:
        self._emissionNFT = emissionNFT

    @property
    def stakeTokenId(self) -> str:
        return self._stakeTokenId
    @stakeTokenId.setter
    def stakeTokenId(self, stakeTokenId: str) -> None:
        self._stakeTokenId = stakeTokenId

class StakePoolContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakedTokenID: str, stakePoolNFT: str) -> None:
        self.nft = stakePoolNFT
        self.stakedTokenId = stakedTokenID
        self.stakeStateNFT = stakeStateNFT
        self.stakePoolKey = stakePoolKey
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakePool.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.nft:
            return False
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        if len(registers[0].getValue()) != 1:
            return False
        return super().validateInputBox(inBox)

    @staticmethod
    def FromStakeStateContract(stakeStateContract: StakeStateContract):
        return StakePoolContract(stakeStateContract.appKit,stakeStateContract.nft,stakeStateContract.stakedTokenId,stakeStateContract.stakePoolNFT)

    @property
    def nft(self) -> str:
        return self._nft
    @nft.setter
    def nft(self, nft: str) -> None:
        self._nft = nft

    @property
    def stakedTokenId(self) -> str:
        return self._stakedTokenId
    @stakedTokenId.setter
    def stakedTokenId(self, stakedTokenId: str) -> None:
        self._stakedTokenId = stakedTokenId

    @property
    def stakeStateNFT(self) -> str:
        return self._stakeStateNFT
    @stakeStateNFT.setter
    def stakeStateNFT(self, stakeStateNFT: str) -> None:
        self._stakeStateNFT = stakeStateNFT

    @property
    def emissionNFT(self) -> str:
        return self._emissionNFT
    @emissionNFT.setter
    def emissionNFT(self, emissionNFT: str) -> None:
        self._emissionNFT = emissionNFT

    @property
    def stakeTokenId(self) -> str:
        return self._stakeTokenId
    @stakeTokenId.setter
    def stakeTokenId(self, stakeTokenId: str) -> None:
        self._stakeTokenId = stakeTokenId

class EmissionContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, _stakeStateNFT: str, _stakeTokenID: str, _stakedTokenID: str, emissionNFT: str) -> None:
        self.nft = emissionNFT
        self.stakedTokenId = _stakedTokenID
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(_stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeTokenID": ErgoAppKit.ergoValue(_stakeTokenID, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakedTokenID": ErgoAppKit.ergoValue(_stakedTokenID, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/emission.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.nft:
            return False
        registers = inBox.getRegisters()
        if len(registers) > 1:
            return False
        if len(registers[0].getValue()) != 4:
            return False
        return super().validateInputBox(inBox)

    def FromStakeStateContract(stakeStateContract: StakeStateContract):
        return EmissionContract(stakeStateContract.appKit,stakeStateContract.nft,stakeStateContract.stakeTokenId,stakeStateContract.stakedTokenId,stakeStateContract.emissionNFT)

    @property
    def nft(self) -> str:
        return self._nft
    @nft.setter
    def nft(self, nft: str) -> None:
        self._nft = nft

    @property
    def stakedTokenId(self) -> str:
        return self._stakedTokenId
    @stakedTokenId.setter
    def stakedTokenId(self, stakedTokenId: str) -> None:
        self._stakedTokenId = stakedTokenId

class StakingIncentiveContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakeTokenID: str, emissionNFT: str, stakePoolKey: str, stakedTokenID: str) -> None:
        self.stakeStateNFT = stakeStateNFT
        self.stakeTokenID = stakeTokenID
        self.emissionNFT = emissionNFT
        self.stakePoolKey = stakePoolKey
        self.stakedTokenID = stakedTokenID
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakeTokenID": ErgoAppKit.ergoValue(stakeTokenID, ErgoValueT.ByteArrayFromHex).getValue(),
            "_emissionNFT": ErgoAppKit.ergoValue(emissionNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakePoolKey": ErgoAppKit.ergoValue(stakePoolKey, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakingIncentive.es"),mapping=mapping)

    def FromStakePoolContract(stakePoolContract: StakePoolContract):
        return StakingIncentiveContract(
            appKit=stakePoolContract.appKit,
            stakeStateNFT=stakePoolContract.stakeStateNFT,
            stakeTokenID=stakePoolContract.stakeTokenId,
            emissionNFT=stakePoolContract.emissionNFT,
            stakePoolKey=stakePoolContract.stakePoolKey,
            stakedTokenID=stakePoolContract.stakedTokenId
        )

    @property
    def stakeStateNFT(self) -> str:
        return self._stakeStateNFT
    @stakeStateNFT.setter
    def stakeStateNFT(self, stakeStateNFT: str) -> None:
        self._stakeStateNFT = stakeStateNFT

    @property
    def stakeTokenID(self) -> str:
        return self._stakeTokenID
    @stakeTokenID.setter
    def stakeTokenID(self, stakeTokenID: str) -> None:
        self._stakeTokenID = stakeTokenID

    @property
    def stakedTokenID(self) -> str:
        return self._stakedTokenID
    @stakedTokenID.setter
    def stakedTokenID(self, stakedTokenID: str) -> None:
        self._stakedTokenID = stakedTokenID

    @property
    def emissionNFT(self) -> str:
        return self._emissionNFT
    @emissionNFT.setter
    def emissionNFT(self, emissionNFT: str) -> None:
        self._emissionNFT = emissionNFT

    @property
    def stakePoolKey(self) -> str:
        return self._stakePoolKey
    @stakePoolKey.setter
    def stakePoolKey(self, stakePoolKey: str) -> None:
        self._stakePoolKey = stakePoolKey

class StakeProxyContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakingIncentiveContract: StakingIncentiveContract) -> None:
        self.stakeStateNFT = stakeStateNFT
        self.stakingIncentiveContract = stakingIncentiveContract

        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingIncentiveContract.contract.getErgoTree().bytesHex())).digest(), ErgoValueT.ByteArray).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakeProxy.es"),mapping=mapping)

    def FromStakingIncentiveContract(stakingIncentiveContract: StakingIncentiveContract):
        return StakeProxyContract(
            appKit=stakingIncentiveContract.appKit,
            stakeStateNFT=stakingIncentiveContract.stakeStateNFT,
            stakingIncentiveContract=stakingIncentiveContract
        )

    def validateInputBox(self, inBox: InputBox) -> bool:
        registers = inBox.getRegisters()
        if len(registers) != 2:
            return False
        return super().validateInputBox(inBox)

    @property
    def stakeStateNFT(self) -> str:
        return self._stakeStateNFT
    @stakeStateNFT.setter
    def stakeStateNFT(self, stakeStateNFT: str) -> None:
        self._stakeStateNFT = stakeStateNFT

    @property
    def stakingIncentiveContract(self) -> StakingIncentiveContract:
        return self._stakingIncentiveContract
    @stakingIncentiveContract.setter
    def stakingIncentiveContract(self, stakingIncentiveContract: StakingIncentiveContract) -> None:
        self._stakingIncentiveContract = stakingIncentiveContract

class AddStakeProxyContract(StakeProxyContract):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakingIncentiveContract: StakingIncentiveContract) -> None:
        self.stakeStateNFT = stakeStateNFT
        self.stakingIncentiveContract = stakingIncentiveContract

        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingIncentiveContract.contract.getErgoTree().bytesHex())).digest(), ErgoValueT.ByteArray).getValue()
        }
        super(ErgoContractBase).__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/addStakeProxy.es"),mapping=mapping)

class UnstakeProxyContract(StakeProxyContract):
    def __init__(self, appKit: ErgoAppKit, stakeStateNFT: str, stakingIncentiveContract: StakingIncentiveContract) -> None:
        self.stakeStateNFT = stakeStateNFT
        self.stakingIncentiveContract = stakingIncentiveContract

        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue(),
            "_stakingIncentiveContract": ErgoAppKit.ergoValue(blake2b(bytes.fromhex(stakingIncentiveContract.contract.getErgoTree().bytesHex())).digest(), ErgoValueT.ByteArray).getValue()
        }
        super(ErgoContractBase).__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/unstakeProxy.es"),mapping=mapping)

class EmissionBox(ErgoBox):
    def __init__(self, appKit: ErgoAppKit, emissionContract: EmissionContract, emissionRemaining: int, amountStaked: int, checkpoint: int, stakers: int, emissionAmount: int) -> None:
        self.emissionContract = emissionContract
        tokens = {self.emissionContract.nft: 1}
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
        amountStaked = int(registers[0].apply(0))
        checkpoint = int(registers[0].apply(1))
        stakers = int(registers[0].apply(2))
        emissionAmount = int(registers[0].apply(3))
        emissionRemaining = int(inputBox.getTokens()[1].getValue())
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
        self.tokens[self.emissionContract.stakedTokenId] = emissionRemaining

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
        self.stakeContract = stakeContract
        tokens = {self.stakeContract.nft: 1, self.stakeContract.stakedTokenId: amountStaked}
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
        checkpoint = int(registers[0].apply(0))
        stakeTime = int(registers[0].apply(1))
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
        self.tokens[self.stakeContract.stakedTokenId] = amountStaked

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
        tokens = {self.stakeStateContract.nft: 1, self.stakeStateContract.stakeTokenId: int(1e9)-stakers}
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
        amountStaked = int(registers[0].apply(0))
        checkpoint = int(registers[0].apply(1))
        stakers = int(registers[0].apply(2))
        checkpointTime = int(registers[0].apply(3))
        cycleDuration = int(registers[0].apply(4))
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
        self.tokens[self.stakeStateContract.stakeTokenId] = int(1e9) - stakers

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
    def __init__(self, appKit: ErgoAppKit, stakePoolContract: StakePoolContract, emissionAmount: int, remaining: int, stakePoolKey: str) -> None:
        self.stakePoolContract = stakePoolContract
        tokens = {self.stakePoolContract.nft: 1, self.stakePoolContract.stakedTokenId: remaining}
        registers = [
            ErgoAppKit.ergoValue([
                emissionAmount
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(stakePoolKey, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e6),stakePoolContract.contract,tokens,registers)

        self._remaining = remaining
        self._emissionAmount = emissionAmount
        self._stakePoolKey = stakePoolKey

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakePoolContact: StakePoolContract):
        registers = inputBox.getRegisters()
        emissionAmount = int(registers[0].apply(0))
        remaining = int(inputBox.getTokens()[1].getValue())
        return StakePoolBox(
            appKit=stakePoolContact.appKit,
            stakePoolContact=stakePoolContact,
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
        self.tokens[self.stakePoolContract.stakedTokenId] = remaining

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
        return StakePoolBox(
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
        tokens = {self.stakeProxyContract.stakingIncentiveContract.stakedTokenID: amountToStake}
        registers = [
            ErgoAppKit.ergoValue([
                stakeTime
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e6),stakeProxyContract.contract,tokens,registers)

        self._amountToStake = amountToStake
        self._userErgoTree = userErgoTree
        self._stakeTime = stakeTime

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeProxyContract: StakeProxyContract):
        registers = inputBox.getRegisters()
        userErgoTree = registers[1].toHex()[4:]
        stakeTime = int(registers[0].apply(0))
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
        self.tokens[self.stakeProxyContract.stakingIncentiveContract.stakedTokenID] = amountToStake

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
        tokens = {stakeBox.stakeKey: 1, self.addStakeProxyContract.stakingIncentiveContract.stakedTokenID: amountToStake}
        registers = [
            ErgoAppKit.ergoValue([
                int(0)
            ],ErgoValueT.LongArray),
            ErgoAppKit.ergoValue(userErgoTree, ErgoValueT.ByteArrayFromHex)
        ]  

        super().__init__(appKit,int(1e6),addStakeProxyContract.contract,tokens,registers)

        self._amountToStake = amountToStake
        self._userErgoTree = userErgoTree
        self._stakeBox = stakeBox

    @staticmethod
    def fromInputBox(inputBox: InputBox, stakeBox: StakeBox, addStakeProxyContract: StakeProxyContract):
        registers = inputBox.getRegisters()
        userErgoTree = registers[1].toHex()[4:]
        amountToStake = int(inputBox.getTokens()[0].getValue())
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
        self.tokens[self.stakeProxyContract.stakingIncentiveContract.stakedTokenID] = amountToStake

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

class EmitTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit, 
            stakeStateInput: InputBox, 
            stakePoolInput: InputBox, 
            emissionInput: InputBox,
            feeInput: List[InputBox],
            stakeStateContract: StakeStateContract,
            stakePoolContract: StakePoolContract,
            emissionContract: EmissionContract,
            changeAddress: str) -> None:
        super().__init__(appKit)
        if not stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not stakePoolContract.validateInputBox(stakePoolInput):
            raise InvalidInputBoxException("Stake pool input box does not match contract")
        if not emissionContract.validateInputBox(emissionInput):
            raise InvalidInputBoxException("Emission input box does not match contract")
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakeStateContract)
        stakePoolBox = StakePoolBox.fromInputBox(stakePoolInput, stakePoolContract)
        emissionBox = EmissionBox.fromInputBox(emissionInput, emissionContract)
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
        self.inputs = [stakeStateInput,stakePoolInput,emissionInput] + feeInput
        self.outputs = [stakeStateBox.outBox,stakePoolBox.outBox,emissionBox.outBox]
        self.fee = int(1e6)
        self.changeAddress = changeAddress

class CompoundTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit,  
            emissionInput: InputBox,
            stakeInputs: List[InputBox],
            feeInput: List[InputBox],
            emissionContract: EmissionContract,
            stakeContract: StakeContract,
            changeAddress: str) -> None:
        super().__init__(appKit)
        if not emissionContract.validateInputBox(emissionInput):
            raise InvalidInputBoxException("Emission input box does not match contract")
        for stakeInput in stakeInputs:
            if not stakeContract.validateInputBox(stakeInput):
                raise InvalidInputBoxException("Stake input box does not match contract")
        emissionBox = EmissionBox.fromInputBox(emissionInput, emissionContract)
        stakeBoxes = []
        stakeRewards = 0
        for stakeInput in stakeInputs:
            box = StakeBox.fromInputBox(stakeInput,stakeContract)
            if box.checkpoint != emissionBox.checkpoint:
                raise InvalidTransactionConditionsException("Stake box not on same checkpoint as emission box")
            box.checkpoint = box.checkpoint + 1
            reward = int(box.amountStaked * emissionBox.emissionAmount / emissionBox.amountStaked)
            stakeRewards += reward
            box.amountStaked += reward
            stakeBoxes.append(box.outBox)

        emissionBox.emissionRemaining -= stakeRewards
        emissionBox.stakers -= len(stakeBoxes)

        self.inputs = [emissionInput] + stakeInputs + feeInput
        self.outputs = [emissionBox.outBox] + stakeBoxes
        self.fee = int(1e6)
        self.changeAddress = changeAddress

class StakeTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit,
            stakeAmount: int,
            stakedTokenName: str,
            stakedTokenDecimals: int,
            stakeStateInput: InputBox,
            feeInput: List[InputBox],
            stakeStateContract: StakeStateContract,
            stakeContract: StakeContract,
            changeAddress: str) -> None:
        super().__init__(appKit)
        if not stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakeStateContract)
        stakeStateBox.amountStaked += stakeAmount
        stakeStateBox.stakers += 1

        userOutput = appKit.mintToken(
            value=int(1e7),
            tokenId=stakeStateInput.getId().toString(),
            tokenName=f'{stakedTokenName} Stake Key',
            tokenDesc=f'{{"originalAmountStaked": {stakeAmount*10**(-1*stakedTokenDecimals)}, "stakeTime": "{datetime.now()}"}}',
            mintAmount=1,
            decimals=0,
            contract=appKit.contractFromTree(feeInput[0].getErgoTree())
        )

        stakeBox = StakeBox(
            appKit=self.appKit,
            stakeContract=stakeContract,
            checkpoint=stakeStateBox.checkpoint,
            stakeTime=int(time()*1000),
            amountStaked=stakeAmount,
            stakeKey=stakeStateInput.getId().toString()
        )

        self.inputs = [stakeStateInput] + feeInput
        self.outputs = [stakeStateBox.outBox, stakeBox.outBox, userOutput]
        self.fee = int(1e6)
        self.changeAddress = changeAddress

class AddStakeTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit,
            addStakeAmount: int,
            stakeStateInput: InputBox,
            stakeInput: InputBox,
            feeInput: List[InputBox],
            stakeStateContract: StakeStateContract,
            stakeContract: StakeContract,
            changeAddress: str) -> None:
        super().__init__(appKit)
        if not stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not StakeContract.validateInputBox(stakeInput):
            raise InvalidInputBoxException("Stake input box does not match contract")
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakeStateContract)
        stakeStateBox.amountStaked += addStakeAmount

        stakeBox = StakeBox.fromInputBox(stakeInput, stakeContract)

        stakeBox.amountStaked += addStakeAmount

        userOutput = ErgoBox(
            appKit=appKit,
            value=int(1e7),
            contract=appKit.contractFromTree(feeInput[0].getErgoTree()),
            tokens={stakeBox.stakeKey: 1}
        )

        self.inputs = [stakeStateInput] + feeInput
        self.outputs = [stakeStateBox.outBox, stakeBox.outBox, userOutput.outBox]
        self.fee = int(1e6)
        self.changeAddress = changeAddress

class UnstakeTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit,
            UnstakeAmount: int,
            stakeStateInput: InputBox,
            stakeInput: InputBox,
            feeInput: List[InputBox],
            stakeStateContract: StakeStateContract,
            stakeContract: StakeContract,
            changeAddress: str) -> None:
        super().__init__(appKit)
        if not stakeStateContract.validateInputBox(stakeStateInput):
            raise InvalidInputBoxException("Stake state input box does not match contract")
        if not StakeContract.validateInputBox(stakeInput):
            raise InvalidInputBoxException("Stake input box does not match contract")
        stakeStateBox = StakeStateBox.fromInputBox(stakeStateInput, stakeStateContract)
        stakeStateBox.amountStaked += addStakeAmount

        stakeBox = StakeBox.fromInputBox(stakeInput, stakeContract)

        stakeBox.amountStaked += addStakeAmount

        userOutput = ErgoBox(
            appKit=appKit,
            value=int(1e7),
            contract=appKit.contractFromTree(feeInput[0].getErgoTree()),
            tokens={stakeBox.stakeKey: 1}
        )

        self.inputs = [stakeStateInput] + feeInput
        self.outputs = [stakeStateBox.outBox, stakeBox.outBox, userOutput.outBox]
        self.fee = int(1e6)
        self.changeAddress = changeAddress
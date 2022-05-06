from hashlib import blake2b
import os
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
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(stakeStateNFT, ErgoValueT.ByteArrayFromHex).getValue()
        }
        super().__init__(appKit,script=os.path.join(os.path.dirname(__file__),"ergoscript/stakePool.es"),mapping=mapping)

    def validateInputBox(self, inBox: InputBox) -> bool:
        tokens = inBox.getTokens()
        if not tokens[0].getId().toString() == self.nft:
            return False
        registers = inBox.getRegisters()
        if len(registers) > 1:
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
    def __init__(self, appKit: ErgoAppKit, stakePoolContract: StakePoolContract, emissionAmount: int, remaining: int) -> None:
        self.stakePoolContract = stakePoolContract
        tokens = {self.stakePoolContract.nft: 1, self.stakePoolContract.stakedTokenId: remaining}
        registers = [
            ErgoAppKit.ergoValue([
                emissionAmount
            ],ErgoValueT.LongArray)
        ]  

        super().__init__(appKit,int(1e6),stakePoolContract.contract,tokens,registers)

        self._remaining = remaining
        self._emissionAmount = emissionAmount

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
            ],ErgoValueT.LongArray)
        ]  

    @property
    def emissionAmount(self) -> int:
        return self._emissionAmount
    @emissionAmount.setter
    def emissionAmount(self, emissionAmount: int) -> None:
        self._emissionAmount = emissionAmount
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

class EmitTransaction(ErgoTransaction):
    def __init__(self, 
            appKit: ErgoAppKit, 
            stakeStateInput: InputBox, 
            stakePoolInput: InputBox, 
            emissionInput: InputBox,
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
        self.inputs = [stakeStateInput,stakePoolInput,emissionInput]
        self.outputs = [stakeStateBox.outBox,stakePoolBox.outBox,emissionBox.outBox]
        self.fee = int(1e6)
        self.changeAddress = changeAddress

    
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT
from paideia_contracts.contracts.ErgoBox import ErgoBox
from paideia_contracts.contracts.staking.EmissionContract import EmissionContract


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
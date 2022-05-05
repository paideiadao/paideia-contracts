from typing import Dict, List
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT
from org.ergoplatform.appkit import ErgoContract, ErgoValue, OutBox

class ErgoBox:
    def __init__(self, appKit: ErgoAppKit, value: int, contract: ErgoContract, tokens: Dict[str, int] = None, registers: List[ErgoValue] = None) -> None:
        self.appKit = appKit
        self.value = value
        self.contract = contract
        self.tokens = tokens
        self.registers = registers

    def outBox(self) -> OutBox:
        return self.appKit.buildOutBox(self.value,self.tokens,self.registers,self.contract)

    @property
    def appKit(self) -> ErgoAppKit:
        return self._appKit
    @appKit.setter
    def appKit(self, appKit: ErgoAppKit) -> None:
        self._appKit = appKit

    @property
    def value(self) -> int:
        return self._value
    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def contract(self) -> ErgoContract:
        return self._contract
    @contract.setter
    def contract(self, contract: ErgoContract) -> None:
        self._contract = contract

    @property
    def tokens(self) -> Dict[str, int]:
        return self._tokens
    @tokens.setter
    def tokens(self, tokens: Dict[str, int]) -> None:
        self._tokens = tokens

    @property
    def registers(self) -> List[ErgoValue]:
        return self._registers
    @registers.setter
    def registers(self, registers: List[ErgoValue]) -> None:
        self._registers = registers
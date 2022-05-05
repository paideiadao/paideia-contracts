import os
from typing import Dict, List
from ergo_python_appkit.appkit import ErgoAppKit, ErgoValueT

from org.ergoplatform.appkit import InputBox

from paideia_contracts.contracts.ErgoContractBase import ErgoContractBase


class EmissionContract(ErgoContractBase):
    def __init__(self, appKit: ErgoAppKit, _stakeStateNFT: str, _stakeTokenID: str, _stakedTokenID: str, emissionNFT: str) -> None:
        self.nft = emissionNFT
        self.stakedTokenId = _stakedTokenID
        mapping = {
            "_stakeStateNFT": ErgoAppKit.ergoValue(_stakeStateNFT, ErgoValueT.ByteArrayFromHex),
            "_stakeTokenID": ErgoAppKit.ergoValue(_stakeTokenID, ErgoValueT.ByteArrayFromHex),
            "_stakedTokenID": ErgoAppKit.ergoValue(_stakedTokenID, ErgoValueT.ByteArrayFromHex)
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
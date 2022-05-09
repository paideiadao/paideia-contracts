from time import time
import traceback
from ergo_python_appkit.appkit import ErgoAppKit
from paideia_contracts.contracts.staking import EmissionBox, EmitTransaction, StakePoolBox, StakeStateBox, StakingIncentiveBox, PaideiaTestConfig

class TestStaking:
    appKit = ErgoAppKit("http://ergolui.com:9053","mainnet","https://api.ergoplatform.com/")
    config = PaideiaTestConfig(appKit)
    txOperator = "9h7L7sUHZk43VQC3PHtSp5ujAWcZtYmWATBH746wi75C5XHi68b"

    def test_emit(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=1,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakePoolInput = StakePoolBox(
            appKit=self.appKit,
            stakePoolContract=self.config.stakePoolContract,
            emissionAmount=293000,
            remaining=900000000
        ).inputBox()
        emissionInput = EmissionBox(
            appKit=self.appKit,
            emissionContract=self.config.emissionContract,
            emissionRemaining=9,
            amountStaked=9569595,
            checkpoint=0,
            stakers=0,
            emissionAmount=293000
        ).inputBox()
        stakingIncentiveInput = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(1e9)
        ).inputBox()
        signed = False
        try:
            unsignedTx = EmitTransaction(
                stakeStateInput=stakeStateInput,
                stakePoolInput=stakePoolInput,
                emissionInput=emissionInput,
                stakingIncentiveInput=stakingIncentiveInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

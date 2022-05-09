from time import time
import traceback
from ergo_python_appkit.appkit import ErgoAppKit
from paideia_contracts.contracts.staking import CompoundTransaction, EmissionBox, EmitTransaction, StakeBox, StakePoolBox, StakeProxyBox, StakeStateBox, StakeTransaction, StakingIncentiveBox, PaideiaTestConfig

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

    def test_compound(self):
        emissionInput = EmissionBox(
            appKit=self.appKit,
            emissionContract=self.config.emissionContract,
            emissionRemaining=293000,
            amountStaked=9569595,
            checkpoint=0,
            stakers=10,
            emissionAmount=293000
        ).inputBox()
        stakeBox1 = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=0,
            stakeTime=0,
            amountStaked=100000,
            stakeKey=self.config.stakedTokenId #this value doesnt matter here
        ).inputBox()
        stakeBox2 = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=0,
            stakeTime=0,
            amountStaked=333333,
            stakeKey=self.config.stakeTokenId #this value doesnt matter here
        ).inputBox()
        stakingIncentiveInput = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(1e9)
        ).inputBox()
        signed = False
        try:
            unsignedTx = CompoundTransaction(
                emissionInput=emissionInput,
                stakeInputs=[stakeBox1,stakeBox2],
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

    def test_stake(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=1,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeProxyInput = StakeProxyBox(
            appKit=self.appKit,
            stakeProxyContract=self.config.stakeProxyContract,
            amountToStake=200000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeTime=int(time()*1000)
        ).inputBox()
        signed = False
        try:
            unsignedTx = StakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeProxyInput=stakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

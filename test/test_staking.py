from time import time
import traceback
from ergo_python_appkit.appkit import ErgoAppKit
from ergo_python_appkit.ErgoBox import ErgoBox
from ergo_python_appkit.ErgoTransaction import ErgoTransaction
from paideia_contracts.contracts.staking import AddStakeProxyBox, AddStakeTransaction, CompoundTransaction, ConsolidateDustTransaction, CreateAddStakeProxyTransaction, EmissionBox, EmitTransaction, StakeBox, StakePoolBox, StakeProxyBox, StakeStateBox, StakeTransaction, StakingIncentiveBox, PaideiaTestConfig, UnstakeProxyBox, UnstakeTransaction
import pytest
from sigmastate.lang.exceptions import InterpreterException

class TestStaking:
    appKit = ErgoAppKit("http://213.239.193.208:9053","mainnet","https://api.ergoplatform.com/")
    config = PaideiaTestConfig(appKit)
    txOperator = "9hxT7sAZEmLWGNp3gN8RRw4qS1NxDMsCtuJkrQ5oEq5w1g7s97U"

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

    def test_emit_initial(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=0,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 3600001),
            amountStaked=10000000,
            cycleDuration=3600000,
            stakers=1
            ).inputBox()
        stakePoolInput = StakePoolBox(
            appKit=self.appKit,
            stakePoolContract=self.config.stakePoolContract,
            emissionAmount=273900000,
            remaining=100000000000
        ).inputBox()
        emissionInput = EmissionBox(
            appKit=self.appKit,
            emissionContract=self.config.emissionContract,
            emissionRemaining=0,
            amountStaked=0,
            checkpoint=-1,
            stakers=0,
            emissionAmount=0
        ).inputBox()
        stakingIncentiveInput = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(1e8)
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

    def test_compound_single(self):
        emissionInput = EmissionBox(
            appKit=self.appKit,
            emissionContract=self.config.emissionContract,
            emissionRemaining=271161000,
            amountStaked=37619804,
            checkpoint=126,
            stakers=2,
            emissionAmount=271161000
        ).inputBox()
        stakeBox1 = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=126,
            stakeTime=0,
            amountStaked=37619804,
            stakeKey=self.config.stakedTokenId #this value doesnt matter here
        ).inputBox()
        stakingIncentiveInput = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(4953000000)
        ).inputBox()
        signed = False
        try:
            unsignedTx = CompoundTransaction(
                emissionInput=emissionInput,
                stakeInputs=[stakeBox1],
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
            emissionRemaining=271161000,
            amountStaked=34206285950,
            checkpoint=126,
            stakers=2,
            emissionAmount=271161000
        ).inputBox()
        stakeBox1 = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=126,
            stakeTime=0,
            amountStaked=37619804,
            stakeKey=self.config.stakedTokenId #this value doesnt matter here
        ).inputBox()
        stakeBox2 = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=126,
            stakeTime=0,
            amountStaked=34168666145,
            stakeKey=self.config.stakeTokenId #this value doesnt matter here
        ).inputBox()
        stakingIncentiveInput = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(4953000000)
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

    def test_add_stake(self):

        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=int(118),
            stakeTime=int(0),
            amountStaked=int(15727686),
            stakeKey="4d82471b2ec40ad3b301dbb5f0e62a5b7edbcdf3ec7dec1324b89f7d5ed65555"
        ).inputBox("8a5917f284b2071db8cbd8cebe9ba793b244d67694ef4382693d0751837e1be4",1)

        assetsRequired = CreateAddStakeProxyTransaction.assetsRequired(self.config, int(10000000), stakeInput)

        userInputs = ErgoBox(appKit=self.appKit,
            value=assetsRequired.nErgRequired,
            contract=self.appKit.dummyContract(),
            tokens={"4d82471b2ec40ad3b301dbb5f0e62a5b7edbcdf3ec7dec1324b89f7d5ed65555": 1, self.config.stakedTokenId: 10000000}).inputBox()
        signedTx = self.appKit.signTransaction(CreateAddStakeProxyTransaction(userInputs=[userInputs],stakeInput=stakeInput,stakingConfig=self.config,amountToStake=int(10000000),address=self.appKit.dummyContract().toAddress().toString()).unsignedTx)

        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=int(118),
            checkpointTime=int(1652691854000),
            amountStaked=int(32016997958),
            cycleDuration=int(3600000),
            stakers=2
            ).inputBox(txId="2f7b078dac5d369c4e1f1c1d9002d4eecf6ee62c3d8fed6579aa015c19133b1c",index=0)
        #addStakeProxyInput = signedTx.getOutputsToSpend()[0]
        addStakeProxyInput = AddStakeProxyBox(
            appKit=self.appKit,
            addStakeProxyContract=self.config.addStakeProxyContract,
            amountToStake=int(10000000),
            userErgoTree="0008cd026443d32bf23bce582b279abd85e128bc26ecb7d8ea1a9ceb87481db90fd80997",
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox("674a706612ab9fa91349dd851dece20a6cb1fed53e27f1733323b8e7d48e04fb",0)
        signed = False
        try:
            unsignedTx = AddStakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                addStakeProxyInput=addStakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

    def test_partial_unstake(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=1,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=1,
            stakeTime=99,
            amountStaked=200000,
            stakeKey=self.config.stakePoolKey
        ).inputBox()
        unstakeProxyInput = UnstakeProxyBox(
            appKit=self.appKit,
            unstakeProxyContract=self.config.unstakeProxyContract,
            amountToUnstake=100000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox()
        signed = False
        try:
            unsignedTx = UnstakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                unstakeProxyInput=unstakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

    def test_full_unstake(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=1,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=1,
            stakeTime=99,
            amountStaked=200000,
            stakeKey=self.config.stakePoolKey
        ).inputBox()
        unstakeProxyInput = UnstakeProxyBox(
            appKit=self.appKit,
            unstakeProxyContract=self.config.unstakeProxyContract,
            amountToUnstake=200000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox()
        signed = False
        try:
            unsignedTx = UnstakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                unstakeProxyInput=unstakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

    def test_add_stake_after_emit(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=2,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=1,
            stakeTime=99,
            amountStaked=100000,
            stakeKey=self.config.stakePoolKey
        ).inputBox()
        addStakeProxyInput = AddStakeProxyBox(
            appKit=self.appKit,
            addStakeProxyContract=self.config.addStakeProxyContract,
            amountToStake=200000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox()

        with pytest.raises(InterpreterException):
            unsignedTx = AddStakeTransaction(
                    stakeStateInput=stakeStateInput,
                    stakeInput=stakeInput,
                    addStakeProxyInput=addStakeProxyInput,
                    stakingConfig=self.config,
                    address=self.txOperator
                ).unsignedTx
            self.appKit.signTransaction(unsignedTx)

    def test_partial_unstake_after_emit(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=2,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=1,
            stakeTime=99,
            amountStaked=200000,
            stakeKey=self.config.stakePoolKey
        ).inputBox()
        unstakeProxyInput = UnstakeProxyBox(
            appKit=self.appKit,
            unstakeProxyContract=self.config.unstakeProxyContract,
            amountToUnstake=100000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox()

        with pytest.raises(InterpreterException):
            unsignedTx = UnstakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                unstakeProxyInput=unstakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx

            self.appKit.signTransaction(unsignedTx)

    def test_full_unstake_after_emit(self):
        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=2,
            checkpointTime=int(self.appKit.preHeader().getTimestamp() - 86400001),
            amountStaked=10000000,
            cycleDuration=86400000,
            stakers=10
            ).inputBox()
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=1,
            stakeTime=99,
            amountStaked=200000,
            stakeKey=self.config.stakePoolKey
        ).inputBox()
        unstakeProxyInput = UnstakeProxyBox(
            appKit=self.appKit,
            unstakeProxyContract=self.config.unstakeProxyContract,
            amountToUnstake=200000,
            userErgoTree=self.appKit.contractFromAddress(self.txOperator).getErgoTree().bytesHex(),
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox()
        with pytest.raises(InterpreterException):
            unsignedTx = UnstakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                unstakeProxyInput=unstakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            ).unsignedTx
            self.appKit.signTransaction(unsignedTx)

    def test_remove_stakepool_funds(self):
        stakePoolInput = StakePoolBox(
            appKit=self.appKit,
            stakePoolContract=self.config.stakePoolContract,
            emissionAmount=293000,
            remaining=900000000
        ).inputBox()
        stakePoolKeyInput = ErgoBox(
            appKit=self.appKit,
            value=int(1e6),
            contract=self.appKit.dummyContract(),
            tokens={self.config.stakePoolKey: 1}
        ).inputBox()
        tokens = {self.config.stakePoolKey: 1}
        for token in stakePoolInput.getTokens():
            tokens[token.getId().toString()] = token.getValue()
        outputBox = ErgoBox(
            appKit=self.appKit,
            value=stakePoolInput.getValue(),
            contract=self.appKit.contractFromAddress(self.txOperator),
            tokens=tokens
        )
        signed = False
        try:
            unsignedTx = ErgoTransaction(self.appKit)
            unsignedTx.inputs=[stakePoolInput,stakePoolKeyInput]
            unsignedTx.outputs=[outputBox.outBox]
            unsignedTx.fee=int(1e6)
            unsignedTx.changeAddress=self.txOperator
            print(ErgoAppKit.unsignedTxToJson(unsignedTx.unsignedTx))
            self.appKit.signTransaction(unsignedTx.unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

    def test_consolidate_dust(self):
        dustInput1 = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(3e6)
        ).inputBox()
        dustInput2 = StakingIncentiveBox(
            appKit=self.appKit,
            stakingIncentiveContract=self.config.stakingIncentiveContract,
            value=int(4e6)
        ).inputBox()
        signed = False
        try:
            unsignedTx = ConsolidateDustTransaction([dustInput1,dustInput2],self.config,self.txOperator).unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)
            signed = True
        except:
            traceback.print_exc()
        assert signed

    def test_steal_stake(self):
        stakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=int(118),
            stakeTime=int(1652544797403),
            amountStaked=int(15727686),
            stakeKey="4d82471b2ec40ad3b301dbb5f0e62a5b7edbcdf3ec7dec1324b89f7d5ed65555"
        ).inputBox("8a5917f284b2071db8cbd8cebe9ba793b244d67694ef4382693d0751837e1be4",1)

        otherStakeInput = StakeBox(
            appKit=self.appKit,
            stakeContract=self.config.stakeContract,
            checkpoint=int(118),
            stakeTime=int(1652544797403),
            amountStaked=int(15727686),
            stakeKey="4d82471b2ec40ad3b301dbb5f0e62a5b7edbcdf3ec7dec1324b89f7d5ed65555"
        ).inputBox("8a5917f284b2071db8cbd8cebe9ba793b244d67694ef4382693d0751837e1ce4",2)

        stakeStateInput = StakeStateBox(
            appKit=self.appKit,
            stakeStateContract=self.config.stakeStateContract,
            checkpoint=int(118),
            checkpointTime=int(1652691854000),
            amountStaked=int(32016997958),
            cycleDuration=int(3600000),
            stakers=2
            ).inputBox(txId="2f7b078dac5d369c4e1f1c1d9002d4eecf6ee62c3d8fed6579aa015c19133b1c",index=0)

        addStakeProxyInput = AddStakeProxyBox(
            appKit=self.appKit,
            addStakeProxyContract=self.config.addStakeProxyContract,
            amountToStake=int(10000000),
            userErgoTree="0008cd026443d32bf23bce582b279abd85e128bc26ecb7d8ea1a9ceb87481db90fd80997",
            stakeBox=StakeBox.fromInputBox(stakeInput, self.config.stakeContract)
        ).inputBox("674a706612ab9fa91349dd851dece20a6cb1fed53e27f1733323b8e7d48e04fb",0)

        stealingOutput = ErgoBox(self.appKit,value=int(1e5),contract=self.appKit.dummyContract(),tokens={otherStakeInput.getTokens()[0].getId(): 1, otherStakeInput.getTokens()[1].getId(): int(15727686)}).outBox

        with pytest.raises(InterpreterException):
            addStakeTransaction = AddStakeTransaction(
                stakeStateInput=stakeStateInput,
                stakeInput=stakeInput,
                addStakeProxyInput=addStakeProxyInput,
                stakingConfig=self.config,
                address=self.txOperator
            )
            addStakeTransaction.inputs.append(otherStakeInput)
            addStakeTransaction.inputs[2] = ErgoBox(self.appKit,value=addStakeProxyInput.getValue(),contract=self.appKit.dummyContract(),
                tokens={addStakeProxyInput.getTokens()[0].getId(): 1, addStakeProxyInput.getTokens()[1].getId(): 10000000},registers=list(addStakeProxyInput.getRegisters())).inputBox()
            addStakeTransaction.outputs.append(stealingOutput)
            unsignedTx = addStakeTransaction.unsignedTx
            print(ErgoAppKit.unsignedTxToJson(unsignedTx))
            self.appKit.signTransaction(unsignedTx)

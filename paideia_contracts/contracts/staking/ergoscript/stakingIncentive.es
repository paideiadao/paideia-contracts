{

    // ===== Contract Information ===== //
    // Name: stakingIncentive
    // Description: Contract that governs the consolidate, emit, compound, and remove funds txs for the staking incentive box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Staking Incentive Box (SELF) ===== //
    // Value: ERG to pay the tx execution bot and the tx mining fee.
    // Registers: None
    // Tokens: None

    // ===== Stake State Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Total Amount Staked
    //     1: Checkpoint
    //     2: Stakers
    //     3: Last Checkpoint Timestamp
    //     4: Cycle Duration 
    // Tokens:
    //   0: 
    //     _1: Stake State NFT  // Identifier for the stake state box.
    //     _2: Amount: 1  
    //   1: 
    //     _1: Stake Token  // Token proving that the stake box was created properly.
    //     _2: Amount: <= 1 Billion

    // ===== Stake Pool Box ===== //
    // Registers:
    //   R4[Long]: Emission Amount
    //   R5[Coll[Byte]]: Stake Pool Key
    // Tokens:
    //   0:
    //     _1: Stake Pool NFT  // Identifier for the stake pool box.
    //     _2: Amount: 1
    //   1:
    //     _1: DAO Token ID  // Token issued by the DAO for distribution
    //     _2: Amount: <= Total DAO Tokens Amount

    // ===== Emission Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Total Amount Staked
    //     1: Checkpoint
    //     2: Stakers
    //     3: Emission Amount
    // Tokens:
    //   0: 
    //     _1: Emission NFT  // Identifier for the emission box.
    //     _2: Amount: 1
    //   1: 
    //     _1: DAO Token ID  // Tokens to be emitted by the DAO.
    //     _2: Amount: <= DAO Token Emission Amount

    // ===== Stake Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Checkpoint
    //     1: Staking Time
    //   R5[Coll[Byte]]: Stake Key ID  // ID of the stake key used for unstaking.
    // Tokens:
    //   0:
    //     _1: Stake Token  // Token proving that the stake box was created properly.
    //     _2: Amount: 1
    //   1:
    //     _1: DAO Token  // Token issued by the DAO, which the user wishes to stake.
    //     _2: Amount: > 0

    // ===== Consolidate Tx ===== //
    // Description: Consolidate all the staking incentive boxes with ERG dust in them into a new staking incentive box.
    // Inputs: StakingIncentiveDustBoxes
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewStakingIncentiveBox, TxOperatorOutputBox

    // ===== Emit Tx ===== //
    // Description: Ran once per day, determining the amount from the stake pool to be withdrawn into a new emission box before being distributed to the stakers.
    // Inputs: StakeStateBox, StakePoolBox, EmissionBox, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewStakeStateBox, NewStakePoolBox, NewEmissionBox, EmissionFeeBox, NewStakingIncentiveBox, TxOperatorOutputBox

    // ===== Compound Tx ===== //
    // Description: Distribute the funds from the new emission box to the stake boxes.
    // Inputs: EmissionBox, StakeBoxes, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewEmissionBox, NewStakeBoxes, NewStakingIncentiveBox, TxOperatorOutputBox

    // ===== Remove Funds Tx ===== //
    // Description: Withdraw funds from the staking incentive boxes.
    // Inputs: StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewStakePoolBox

    // ===== Hard-Coded Constants ===== //
    val EmissionNFT: Coll[Byte]           = _emissionNFT               // Identifier for the emission box
    val StakeStateNFT: Coll[Byte]         = _stakeStateNFT             // Identifier for the stake state box
    val StakeTokenID: Coll[Byte]          = _stakeTokenID              // Token proving that the stake box was created properly
    val StakePoolKey: Coll[Byte]          = _stakePoolKey              // Stake pool key used for accessing the stake pool box funds
    val DustCollectionReward: Long        = _dustCollectionReward      // Dust consolidation tx reward for the execution bot
    val DustCollectionMinerFee: Long      = _dustCollectionMinerFee    // Dust consolidation tx miner fee
    val EmitReward: Long                  = _emitReward                // Emit tx reward for the execution bot
    val EmitMinerFee: Long                = _emitMinerFee              // Emit tx miner fee
    val BaseCompoundReward: Long          = _baseCompoundReward        // Base compound tx reward for the execution bot
    val BaseCompoundMinerFee: Long        = _baseCompoundMinerFee      // Base compound tx miner fee
    val VariableCompoundReward: Long      = _variableCompoundReward    // Variable compound tx reward for the excution bot
    val VariableCompoundMinerFee: Long    = _variableCompoundMinerFee  // Variable compound tx miner fee
    val StakingIncentiveBoxMaxValue: Long = 100000000                  // Max value the staking incentive box can have

    // ===== Perform Consolidate Tx ===== //

    // Conditions for a valid consolidate tx
    val validConsolidateTx: Boolean = {

        // Condition for a consolidation tx to occur
        val isConsolidateTx: Boolean = {
            allOf(Coll(
                (SELF.value <= StakingIncentiveBoxMaxValue),
                (OUTPUTS.size == 3)
            ))
        }

        if (isConsolidateTx) {

            //Consolidate Tx Variables
            val stakingIncentiveDustBoxesAmount: Int = INPUTS.filter({(input: Box) => (input.propositionBytes == SELF.propositionBytes)}).size
            val consolidateRewardAmount: Long = DustCollectionReward * stakingIncentiveDustBoxesAmount
            
            //Consolidate Tx Outputs
            val newStakingIncentiveBox: Box = OUTPUTS(0)
            val txOperatorOutputBox: Box = OUTPUTS(1)
            val minerFeeBox: Box = OUTPUTS(2)

            // Conditions for a valid staking incentive output box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value > SELF.value),                        // Check that the new incentive box has increased ERG
                    (newStakingIncentiveBox.propositionBytes == SELF.propositionBytes)  // Check that the new incentive box is guarded by the same contract
                ))
            }

            // Conditions for a valid tx operator output box
            val validTxOperatorOutputBox: Boolean = {
                (txOperatorOutputBox.value == consolidateRewardAmount)  // Check that the tx operator receives the correct amount of rewards
            }

            // Conditions for a valid consolidate tx miner fee box
            val validMinerFeeBox: Boolean = {
                (minerFeeBox.value == DustCollectionMinerFee)  // The default miner fee for the consolidation tx
            }

            allOf(Coll(
                validNewStakingIncentiveBox,
                validTxOperatorOutputBox,
                validMinerFeeBox
            ))

        } else {
            false
        }

    }

    // ====== Perform Emit Tx ===== //

    // Conditions for a valid emit tx
    val validEmitTx: Boolean = {

        // Conditions for valid inputs to the emit tx
        val validEmitInputs: Boolean = {

            // Check INPUTS size
            if (INPUTS.size >= 3) {

                // Emit Tx Inputs
                val stakeStateBox: Box = INPUTS(0)
                val emissionBox: Box = INPUTS(2)

                allOf(Coll(

                    // Check that the input stake state box contains the NFT identifier
                    (stakeStateBox.tokens.getOrElse(0, (Coll[Byte](), 0L))._1 == StakeStateNFT),

                    // Check that the input emission box contains the NFT identifier
                    (emissionBox.tokens.getOrElse(0, (Coll[Byte](), 0L))._1 == EmissionNFT),

                    // Check that the current staking incentive box is part of the emit tx inputs
                    (INPUTS(INPUTS.size-1).id == SELF.id)

                ))

            } else {
                false
            }

        }

        if (validEmitInputs) {

            // Emit Tx Outputs
            val newStakingIncentiveBox: Box = OUTPUTS(4)
            val txOperatorOutputBox: Box = OUTPUTS(5)
            val minerFeeBox: Box = OUTPUTS(6)

            // Conditions for a valid new staking incentive box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value >= SELF.value - EmitReward - EmitMinerFee - 1000000),  // Check that the new staking incentive box can provide the necessary rewards
                    (newStakingIncentiveBox.propositionBytes == SELF.propositionBytes)                   // Check that the new staking incentive box is guarded by the same contract
                ))
            }

            // Conditions for a valid tx operator output box
            val validTxOperatorOutputBox: Boolean = {
                (txOperatorOutputBox.value == EmitReward)  // Tx operator gets the default reward for executing the emit tx
            }
            
            // Conditions for a valid emit tx miner fee box
            val validMinerFeeBox: Boolean = {
                (minerFeeBox.value == EmitMinerFee)  // Miner receives the default emit miner fee reward
            }

            allOf(Coll(
                validNewStakingIncentiveBox,
                validTxOperatorOutputBox,
                validMinerFeeBox
            ))


        } else {
            false
        }

    }


    // ===== Perform Compound Tx ===== //

    // Conditions for a valid compound tx
    val validCompoundTx: Boolean = {

        // Compound Tx Inputs
        val emissionBox: Box = INPUTS(0)
        
        // Conditions for valid emit tx inputs
        val validCompoundInputs: Boolean = {

            allOf(Coll(

                // Check that the input emission box contains the NFT identifier
                (emissionBox.tokens.getOrElse(0, (Coll[Byte](), 0L))._1 == EmissionNFT),

                // Check that the current staking incentive box is part of the emit tx inputs
                (INPUTS(INPUTS.size-1).id == SELF.id)

            ))

        }

        if (validCompoundInputs) {

            // Compound Tx Variables
            val stakeBoxesAmount: Int = INPUTS.filter({(input: Box) => 

                // Check if the input box has tokens in it
                if (input.tokens.size > 0) {

                    allOf(Coll(

                        // Check of the first token is the stake token identifier (i.e. it is a stake box)
                        (input.tokens(0)._1 == StakeTokenID),

                        // Check to see if the input stake box has the same emission cycle checkpoint as the emission box
                        (input.R4[Coll[Long]].get(0) == emissionBox.R4[Coll[Long]].get(1))

                    ))
            
                } else {
                    false
                }
            
            }).size

            val compoundReward: Long = BaseCompoundReward + (VariableCompoundReward * stakeBoxesAmount)
            val compoundMinerFee: Long = BaseCompoundMinerFee + (VariableCompoundMinerFee * stakeBoxesAmount)

            // Compound Tx Outputs
            val newStakingIncentiveBox: Box = OUTPUTS(INPUTS.size-1)
            val txOperatorOutputBox: Box = OUTPUTS(INPUTS.size)
            val minerFeeBox: Box = OUTPUTS(INPUTS.size+1)

            // Conditions for a valid number of input boxes into the compound tx
            val validNumberOfInputs: Boolean = {
                (INPUTS.size == stakeBoxesAmount+2)
            }

            // Conditions for a valid new staking incentive output box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value >= SELF.value - compoundReward - compoundMinerFee),  // Check that the new staking incentive box can provide the compound tx rewards
                    (newStakingIncentiveBox.propositionBytes == SELF.propositionBytes)                 // Check that the new staking incentive box is guarded by the same contract
                ))
            }

            // Conditions for a valid tx operator output box
            val validTxOperatorOutputBox: Boolean = {
                (txOperatorOutputBox.value == compoundReward)  // Tx operator receives their reward for executing the compound tx
            }

            // Conditions for a valid compound tx miner fee box
            val validMinerFeeBox: Boolean = {
                (minerFeeBox.value == compoundMinerFee)  // Miner receives the calculated miner fee reward for the compound tx
            }

            allOf(Coll(
                validNumberOfInputs,
                validNewStakingIncentiveBox,
                validTxOperatorOutputBox,
                validMinerFeeBox
            ))

        } else {
            false
        }

    }

    // ===== Perform Remove Funds Tx ===== //

    // Check conditions for a valid remove funds tx
    val validRemoveFundsTx: Boolean = {

        if (!(validConsolidateTx || validEmitTx || validCompoundTx)) {

            // Stake Pool Key Tx Output
            val outputBoxWithStakePoolKey: Box = OUTPUTS(0)

            // Check to see if the output box has the stake pool key
            (outputBoxWithStakePoolKey.tokens(0)._1 == StakePoolKey)

        } else {
            false
        }

    }

    sigmaProp(validConsolidateTx || validEmitTx || validCompoundTx || validRemoveFundsTx)

}
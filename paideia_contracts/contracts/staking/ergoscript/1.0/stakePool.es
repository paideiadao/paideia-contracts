{
    
    // ===== Contract Information ===== //
    // Name: stakePool
    // Description: Contract that governs the emit and remove funds transactions for the stake pool box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Stake Pool Box (SELF) ===== //
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

    // ===== Emission Fee Box ===== //
    // Tokens:
    //   0:
    //     _1: DAO Token  // Token issued by the DAO.
    //     _2: Amount: 1% fee
    //			

    // ===== Emit Tx ===== //
    // Description: Ran once per day, determining the amount from the stake pool to be withdrawn into a new emission box before being distributed to the stakers.
    // Inputs: StakeStateBox, StakePoolBox, EmissionBox, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewStakeStateBox, NewStakePoolBox, NewEmissionBox, EmissionFeeBox, StakingIncentiveBox, TxOperatorOutput

    // ===== Remove Funds Tx ===== //
    // Description: Removing funds from the stake pool box.
    // Inputs: StakePoolBox, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: A box with the Stake Pool Key as a token in it, any other box.

    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT:      Coll[Byte] = _stakeStateNFT       // NFT identifying the stake state box
    val EmissionFeeAddress: Coll[Byte] = _emissionFeeAddress  // Address where the emission fee is sent

    // ===== Perform Emit Tx ===== //
    
    // Check conditions for a valid Emit Tx
    val validEmitTx: Boolean = {

        // Emit Tx Inputs
        val stakeStateBox: Box = INPUTS(0)
        val stakePoolBox:  Box = INPUTS(1)

        // Check conditions for valid inputs into the emit tx
        val validEmitInputs: Boolean = {

            allOf(Coll(
                (stakeStateBox.tokens(0)._1 == StakeStateNFT),  // Check that the stake state box contains the correct NFT identifier
                (stakePoolBox.id == SELF.id)                    // Check that the second input box is the current stake pool box with the correct box id
            ))

        }

        if (validEmitInputs) {
            // Emit Tx Inputs
            val emissionBox:      Box = INPUTS(2)

            // Emit Tx Outputs
            val newStakeStateBox: Box = OUTPUTS(0)
            val newStakePoolBox:  Box = OUTPUTS(1)
            val newEmissionBox:   Box = OUTPUTS(2)
            val emissionFeeBox:   Box = OUTPUTS(3)
                
            // Get the amount of tokens alloted for emission
            val emissionAmount : Long = SELF.R4[Coll[Long]].get(0)

            // Calculate the leftover dust tokens within the emission box
            val emissionDust: Long = if (emissionBox.tokens.size >= 2) emissionBox.tokens(1)._2 else 0L

            // Calculate the remaining stake pool tokens along with the leftover emission box dust
            val remainingStakePoolTokensAndEmissionDust: Long = SELF.tokens(1)._2 + emissionDust

            // Get the total amount staked since the previous snapshot from the stake state box
            val totalAmountStaked: Long = stakeStateBox.R4[Coll[Long]].get(0)

            // The emisson fee taken from the stake pool is 1% of the alloted emission amount 
            val emissionFeeAmount: Long = emissionAmount / 100L

            // Check for that a valid new stake pool box was created as an output
            val validNewStakePoolBox: Boolean = {

                // Check if the output stakepool box has the correct amount of tokens remaining after the emit tx
                val validRemainingStakePoolTokensAmount: Boolean = {

                    // Check if the alloted emission amount of tokens needs to be taken out of the stake pool
                    if (remainingStakePoolTokensAndEmissionDust > emissionAmount) {

                        allOf(Coll(

                            // DAO tokens used for emission
                            (newStakePoolBox.tokens(1)._1 == SELF.tokens(1)._1),
                            (newStakePoolBox.tokens(1)._2 == remainingStakePoolTokensAndEmissionDust - emissionAmount)

                        ))

                    } else {
                        (newStakePoolBox.tokens.size == 1) // No more DAO tokens
                    }

                }
                
                allOf(Coll(

                    // Check that the new stake pool box value is preserved
                    (newStakePoolBox.value == SELF.value),

                    // Check that the new stake pool box has the same contract
                    (newStakePoolBox.propositionBytes == SELF.propositionBytes),

                    // Check that the stake pool nft identifier is the same
                    (newStakePoolBox.tokens(0)._1 == SELF.tokens(0)._1),

                    // Make sure that the remaining stake pool token amount is appropriate depending on if emission is still possible
                    validRemainingStakePoolTokensAmount,
                    
                    // Check that the new stake pool box has the same alloted emission amount as the current one
                    (newStakePoolBox.R4[Coll[Long]].get == SELF.R4[Coll[Long]].get),
                    
                    // Check that the DAO token id is the same for the new stake pool box
                    (newStakePoolBox.R5[Coll[Byte]].get == SELF.R5[Coll[Byte]].get),

                    // Update the total amount of staked tokens after the emit tx
                    (newStakeStateBox.R4[Coll[Long]].get(0) == (totalAmountStaked + (emissionAmount - emissionFeeAmount) - emissionDust))
                
                ))

            }

            // Check that a valid emission fee box was created as an output
            val validEmissionFeeBox: Boolean = {

                // An emission fee box is created only if there are any remaining tokens in the stake pool to be used for emission
                if (newStakePoolBox.tokens.size > 1) {
                        
                    allOf(Coll(
                        (emissionFeeBox.propositionBytes == EmissionFeeAddress),  // Check contract bytes
                        (emissionFeeBox.value == 1000000),                        // Minimum ERG value for box to exists
                        (emissionFeeBox.tokens(0)._1 == SELF.tokens(1)._1),       // DAO Token ID
                        (emissionFeeBox.tokens(0)._2 == emissionFeeAmount)        // 1% fee of DAO tokens
                    ))

                } else {
                    true
                }

            }

            allOf(Coll(
                validNewStakePoolBox,
                validEmissionFeeBox
            ))

        } else {
            false
        }

    }

    // ===== Perform Remove Funds Tx ===== //

    // Check conditions for a valid remove funds tx
    val validRemoveFundsTx: Boolean = {

        // Remove Funds Tx Inputs
        val stakePoolBox: Box = INPUTS(0)

        // Remove Funds Tx Outputs
        val outputBoxWithStakePoolKey: Box = OUTPUTS(0)

        // Check that the inputs to the remove funds tx are valid
        val validRemoveFundsInput: Boolean = {
            (stakePoolBox.id == SELF.id)
        }

        if (validRemoveFundsInput) {

            // Check that the first output has the stake pool key as a token id
            (outputBoxWithStakePoolKey.tokens(0)._1 == SELF.R5[Coll[Byte]].get)

        } else {
            false
        }

    }
    
    sigmaProp(validEmitTx || validRemoveFundsTx)

}
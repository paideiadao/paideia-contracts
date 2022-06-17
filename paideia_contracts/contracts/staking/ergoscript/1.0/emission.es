{
    
    // ===== Contract Information ===== //
    // Name: emission
    // Description: Contract that governs the emit and compound transactions for the emission box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Emission Box (SELF) ===== //
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

    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT: Coll[Byte] = _stakeStateNFT  // NFT identifying the stake state box
    val StakeTokenID:  Coll[Byte] = _stakeTokenID   // Token proving that the stake box was created properly
    val StakedTokenID: Coll[Byte] = _stakedTokenID  // Token identifier for the token distributed by the DAO

    // ===== Perform Emit Tx ===== //

    // Check conditions for a valid Emit Tx
    val validEmitTx: Boolean = {

        // Emit Tx Inputs
        val stakeStateBox: Box = INPUTS(0)
        val stakePoolBox: Box = INPUTS(1)     
        val emissionBox: Box = INPUTS(2)

        // Emit Tx Outputs
        val newStakeStateBox: Box = OUTPUTS(0)
        val newStakePoolBox: Box = OUTPUTS(1)
        val newEmissionBox: Box = OUTPUTS(2)

        // Check conditions for valid inputs
        val validEmitInputs: Boolean = {

            allOf(Coll(
                (stakeStateBox.tokens(0)._1 == StakeStateNFT),  // Check that the stake state box contains the correct NFT identifier
                (emissionBox.id == SELF.id)                     // Check that the third input box is the current emission box with the correct box id
            ))

        }

        if (validEmitInputs) {

            // Check conditions for a valid new emission box
            val validNewEmissionBox: Boolean = {

                // Calculate the remaining stake pool tokens and the leftover dust tokens within the current emission box
                val remainingStakePoolTokensAndEmissionDust: Long = stakePoolBox.tokens(1)._2 + SELF.tokens.getOrElse(1,(Coll[Byte](),0L))._2

                allOf(Coll(

                    // Check that the new emission box value is the same as the current box
                    (newEmissionBox.value == SELF.value),

                    // Check that the new emission box is governed by the same contract as this current emission box
                    (newEmissionBox.propositionBytes == SELF.propositionBytes),

                    // Check that the Total Amount Staked, Checkpoint, and Stakers values in the new emission box are the same as the input stake state box
                    (newEmissionBox.R4[Coll[Long]].get.slice(0, 3) == stakeStateBox.R4[Coll[Long]].get.slice(0, 3)),
                    
                    // Update the emission amount of the new emission box, which will contain 99% of the allotted emission amount designated within R4 of the stake pool box - the remaining 1% goes to the ErgoPad treasury
                    (newEmissionBox.R4[Coll[Long]].get(3) == (if (stakePoolBox.R4[Coll[Long]].get(0) < remainingStakePoolTokensAndEmissionDust) (stakePoolBox.R4[Coll[Long]].get(0) - (stakePoolBox.R4[Coll[Long]].get(0) / 100L)) else remainingStakePoolTokensAndEmissionDust)),
                
                    // Check that the new emission box contains the same emission NFT token id as the current emission box
                    (newEmissionBox.tokens(0)._1 == SELF.tokens(0)._1),

                    // Check that the new emission box contains the same issued DAO token id as the current emission box
                    (newEmissionBox.tokens(1)._1 == StakedTokenID),

                    // Check that the new emission box contains the same amount of emission DAO tokens designated within R4 of the new emission box, which corresponds to the allotted emission amount designated within R4 of the stake pool box
                    (newEmissionBox.tokens(1)._2 == newEmissionBox.R4[Coll[Long]].get(3)) 

                ))

            }

            validNewEmissionBox
            
        } else {
            false
        }

    }

    // ===== Perform Compound Tx ===== //

    // Check conditions for a valid compound tx
    val validCompoundTx: Boolean = {

        // Compound Tx Inputs
        val emissionBox: Box = INPUTS(0)

        // Compound Tx Outputs
        val newEmissionBox: Box = OUTPUTS(0)

        // Check for a valid compound tx input
        val validCompoundInput: Boolean = {

            // Check that the first input box is the current emission box with the same box id
            (emissionBox.id == SELF.id)

        }

        if (validCompoundInput) {

            // Get stake boxes with the same checkpoint time as the current emission box
            val stakeBoxes: Coll[Box] = INPUTS.filter({(stakeBox: Box) => if (stakeBox.tokens.size > 0) (stakeBox.tokens(0)._1 == StakeTokenID) && (stakeBox.R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(1)) else false})
            
            // Check for valid emission output box
            val validNewEmissionBox: Boolean = {

                // Check that the correct amount of emission tokens are remaining
                val validRemainingEmission: Boolean = {
                    
                    // Calculate emission amount, total distributed amount, and the remaining emission amount
                    val emissionAmount: BigInt = SELF.R4[Coll[Long]].get(3).toBigInt
                    val distributedAmount: BigInt = stakeBoxes.fold(0.toBigInt, {(acc: BigInt, stakeBox: Box) => acc + ((stakeBox.tokens(1)._2.toBigInt * emissionAmount) / SELF.R4[Coll[Long]].get(0).toBigInt)})
                    val remainingEmission: BigInt = SELF.tokens(1)._2 - distributedAmount

                    // Check if the amount of emission tokens for this current emission box is less than the total distributed amount
                    if (SELF.tokens(1)._2 <= distributedAmount) {

                        // There should not be any emission tokens in the new emission box
                        (newEmissionBox.tokens.size == 1)

                    } else {

                        // The new emission box contains the remaining emission tokens after distribution
                        (newEmissionBox.tokens(1)._1 == StakedTokenID) && (newEmissionBox.tokens(1)._2 >= remainingEmission)

                    }

                }

                allOf(Coll(

                    // Check that the new emission box has the same value as the current box
                    (newEmissionBox.value == SELF.value),

                    // Check that the new emission box is governed by the same contract as this current emission box
                    (newEmissionBox.propositionBytes == SELF.propositionBytes),

                    // Check that the new emission box contains the same emission NFT token id as the current emission box
                    (newEmissionBox.tokens(0)._1 == SELF.tokens(0)._1),

                    // Check for the correct amount of remaining tokens in the new emission box
                    validRemainingEmission,

                    // Check that the new emission box maintains the same Total Amount Staked and Checkpoint time
                    (newEmissionBox.R4[Coll[Long]].get.slice(0, 2) == SELF.R4[Coll[Long]].get.slice(0, 2)),

                    // Check that the amount of stakers who received funds are substracted from the total of the current cycle
                    (newEmissionBox.R4[Coll[Long]].get(2) == SELF.R4[Coll[Long]].get(2) - stakeBoxes.size),

                    // Check that the allotted emission amount remains the same for the new emission box
                    (newEmissionBox.R4[Coll[Long]].get(3) == SELF.R4[Coll[Long]].get(3)) 

                ))

            }

            validNewEmissionBox

        } else {
            false
        }

    }

    sigmaProp(validEmitTx || validCompoundTx)

}
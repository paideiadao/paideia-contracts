{

    // ===== Contract Information ===== //
    // Name: stake
    // Description: Contract that governs the compound, unstake, and add stake txs for the stake box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Stake Box (SELF) ===== //
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

    // ===== Unstake Proxy Box ===== //
    // Registers:
    //  R4[Coll[Long]]:
    //    0: Amount to unstake
    //  R5[Coll[Byte]]: User ErgoTree bytes (i.e. PK)
    // Tokens:
    //  0:
    //    _1: Stake Key  // Sent from the user to the unstake proxy box
    //    _2: Amount: 1

    // ===== Add Stake Proxy Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Staketime
    //   R5[Coll[Byte]]: User ErgoTree bytes
    // Tokens:
    //  0:
    //    _1: Stake Key  // NFT used as a key for adding stake as well as unstaking
    //    _2: Amount: 1
    //  1:
    //    _1: DAO Token  // Token issued by the DAO, which the user wishes to stake.
    //    _2: Amount: > 0 amount that the uers owns and wants to additionally stake.

    // ===== Compound Tx ===== //
    // Description: Distribute the funds from the new emission box to the stake boxes.
    // Inputs: EmissionBox, StakeBoxes, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewEmissionBox, NewStakeBoxes, NewStakingIncentiveBox, TxOperatorOutputBox

    // ===== Stake Tx ===== //
    // Description: User sends DAO tokens to the stake box and receive a stake key in return, proving they have staked and used for unstaking.
    // Inputs: 
    //   Stake: StakeStateBox, StakeProxyBox
    //   Add Stake: StakeStateBox, StakeBox, AddStakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: 
    //   Stake: NewStakeStateBox, NewStakeBox, UserWalletBox
    //   Add Stake: NewStakeStateBox, NewStakeBox, UserWalletBox 

    // ===== Unstake Tx ===== //
    // Description: User wishes to remove their staked tokens from the staking protocol, using their stake key.
    // Inputs: StakeStateBox, StakeBox, UnstakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: 
    //   Full Unstake: NewStakeStateBox, UserWalletBox
    //   Partial Unstake: NewStakeStateBox, UserWalletBox, NewStakeBox

    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT: Coll[Byte] = _stakeStateNFT  // Identifier for the stake state box
    val EmissionNFT: Coll[Byte]   = _emissionNFT    // Identifier for the emission box

    // Stake box parameters
    val checkpoint: Long = SELF.R4[Coll[Long]].get(0)    // Emission cycle checkpoint
    val stakingTime: Long = SELF.R4[Coll[Long]].get(1)   // Time when stake occured
    val stakeKey: Coll[Byte] = SELF.R5[Coll[Byte]].get   // Stake key NFT id  
    val stakedAmount: Long = SELF.tokens(1)._2.toBigInt  // Amount of DAO tokens staked by the user in the stake box

    // ===== Perform Compount Tx ===== //

    // Check conditions for a valid compount tx
    val validCompoundTx: Boolean = {

        // Compound Tx Inputs
        val emissionBox: Box = INPUTS(0)

        // Conditions for valid compound tx inputs
        val validCompoundTxInput: Boolean = {
            (emissionBox.tokens(0)._1 == EmissionNFT)  // Check that the first input holds the emission box identifier NFT
        }

        if (validCompoundTxInput) {

            // Compount Tx variables
            val totalAmountStaked: Long = emissionBox.R4[Coll[Long]].get(0)               // Get the total amount staked parameter from the emission box
            val emissionAmount: BigInt = emissionBox.R4[Coll[Long]].get(3).toBigInt       // Get the alloted emission amount parameter from the emission box
            val rewardAmount: Long = (emissionAmount * stakedAmount) / totalAmountStaked  // Reward amount given to staker for the compound tx
            val stakeBoxIndex: Long = INPUTS.indexOf(SELF, 1)                             // Get the index of the current stake box  

            // Compount Tx Ouputs
            val newStakeBox: Box = OUTPUTS(stakeBoxIndex)  // Get the index of the new stake box, this only works since the ordering of the new emission box and the new stake boxes is the same as the inputs

            // Check that the new stake box is produced properly
            val validSelfReplication: Boolean = {

                allOf(Coll(
                    
                    // Check that the new stake box value is preserved
                    (newStakeBox.value == SELF.value),                

                    // Check that the new stake box is guarded by the same contrat              
                    (newStakeBox.propositionBytes == SELF.propositionBytes),

                    // Check that the emission cycle checkpoint increases
                    (newStakeBox.R4[Coll[Long]].get(0) == checkpoint + 1),

                    // Check that the stake time parameter is kept in the new stake box
                    (newStakeBox.R4[Coll[Long]].get(1) == stakingTime),

                    // Check that the stake key NFT id is still saved in the new stake box
                    (newStakeBox.R5[Coll[Byte]].get == stakeKey),

                    // Checl that the new stake box keeps the same stake token 
                    (newStakeBox.tokens(0)._1 == SELF.tokens(0)._1),
                    (newStakeBox.tokens(0)._2 == SELF.tokens(0)._2),

                    // Check that the new stake box receives the DAO token staking reward amount
                    (newStakeBox.tokens(1)._1 == SELF.tokens(1)._1),
                    (newStakeBox.tokens(1)._2 == SELF.tokens(1)._2 + rewardAmount)

                ))

            }
            
            // The stake box only checks that the new stake box is replicated properly in the compound tx
            validSelfReplication

        } else {
            false
        }

    }

    // ===== Perform Unstake Tx ===== //

    // Conditions for a valid unstake tx
    val validUnstakeTx: Boolean = {

        // Unstake Tx Inputs
        val stakeStateBox: Box = INPUTS(0)
        val stakeBox: Box = INPUTS(1)

        // Unstake Tx Outputs
        val newStakeStateBox: Box = OUTPUTS(0)
        val userWalletBox: Box = OUTPUTS(1)

        // Conditions for the valid inputs of the unstake tx
        val validUnstakeInputs: Boolean = {

            allOf(Coll(

                // Check that the input stake state box has the correct NFT identifier
                (stakeStateBox.tokens(0)._1 == StakeStateNFT),

                // Check that the input stake box is the current box by verifying the box id
                (stakeBox.id == SELF.id),

                // Check that the total amount staked in the staking protocol has decreased after the unstake tx
                (newStakeStateBox.R4[Coll[Long]].get(0) < stakeStateBox.R4[Coll[Long]].get(0))

            ))

        }

        if (validUnstakeInputs) {

            // Partial Unstake Tx Outputs
            val newStakeBox: Box = OUTPUTS(2)
            
            // Check conditions for a partial unstake tx
            val isPartialUnstake: Boolean = {
                (newStakeBox.propositionBytes == SELF.propositionBytes)  // Check that the new stake box is guarded by the same contract
            }

            if (isPartialUnstake) {

                // Conditions for valid replication of the new stake box for a partial unstake
                val validSelfReplication: Boolean = {

                    // Check that the new stake box contains a reference to the stake key NFT id
                    if (newStakeBox.R5[Coll[Byte]].isDefined) {
                        (newStakeBox.R5[Coll[Byte]].get == stakeKey)
                    } else {
                        false  // Partial unstake tx will fail if the new stake box is not replicated properly
                    }

                }

                // Conditions for the user wallet output box
                val validUserWalletBox: Boolean = {
                    (userWalletBox.tokens(1)._1 == SELF.R5[Coll[Byte]].get)  // Check that the user wallet box contains the stake key again
                }

                allOf(Coll(
                    validSelfReplication,
                    validUserWalletBox
                ))

            } else {
                true  // Having valid inputs to the unstake tx is the only thing needed for a valid unstake tx.
            }

        } else {
            false
        }

    }

    // ===== Perform Add Stake Tx ===== //

    // Conditions for a valid add stake tx
    val validAddStakeTx: Boolean = {

        // Add Stake Tx Inputs
        val stakeStateBox: Box = INPUTS(0)
        val stakeBox: Bos = INPUTS(1)

        // Conditions for valid inputs to the add stake tx
        val validAddStakeInputs: Boolean = {
            allOf(Coll(
                (stakeStateBox.tokens(0)._1 == StakeStateNFT),  // Check that the input stake state box has the correct NFT identifier
                (stakeBox.id == SELF.id)                        // Check that the stake box is the current box with the same box id
            ))

        }

        // The stake box contract only checks for valid inputs to the add stake tx
        validAddStakeInputs

    }

    sigmaProp(validCompoundTx || validUnstakeTx || validAddStakeTx)

}
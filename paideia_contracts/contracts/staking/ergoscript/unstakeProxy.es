{

    // ===== Contract Information ===== //
    // Name: UnstakeStakeProxy
    // Description: Proxy contract that the user sends their stake token to, it governs the unstake tx and refund tx for the unstake proxy box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Unstake Proxy Box (SELF) ===== //
    // Registers:
    //  R4[Coll[Long]]:
    //    0: Unstake Amount
    //  R5[Coll[Byte]]: User ErgoTree Bytes (i.e. PK)
    // Tokens:
    //  0:
    //    _1: Stake Key  // Sent from the user to the unstake proxy box
    //    _2: 1

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
    //     _2: 1  
    //   1: 
    //     _1: Stake Token  // Token proving that the stake box was created properly.
    //     _2: <= 1 Billion

    // ===== Stake Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Checkpoint
    //     1: Staking Time
    //   R5[Coll[Byte]]: Stake Key ID  // ID of the stake key used for unstaking.
    // Tokens:
    //   0:
    //     _1: Stake Token  // Token proving that the stake box was created properly.
    //     _2: 1
    //   1:
    //     _1: DAO Token  // Token issued by the DAO, which the user wishes to stake.
    //     _2: > 0

    // ===== Unstake Tx ===== //
    // Description: User wishes to remove their staked tokens from the staking protocol, using their stake key.
    // Inputs: StakeStateBox, StakeBox, UnstakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: 
    //   Full Unstake: NewStakeStateBox, UserWalletBox
    //   Partial Unstake: NewStakeStateBox, UserWalletBox, NewStakeBox

    // ===== Refund Tx ===== //
    // Description: Return the stake key back to the user wallet.
    // Inputs: UnstakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: UserWalletBox
    
    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT: Coll[Byte] =                _stakeStateNFT             // NFT identifying the stake state box
    val StakingIncentiveContractHash: Coll[Byte] = _stakingIncentiveContract  // Blake2b256 hash of the staking incentive contract
    val ToStakingIncentive: Long =                 _toStakingIncentive        // Amount of ERG to insert into the staking incentive output
    val ExecutorReward: Long =                     _executorReward            // Reward for the tx execution bot
    val MinerFee: Long =                           _minerFee                  // Miner fee reward

    // ===== Relevant Variables ===== //
    val userPropositionBytes: Coll[Byte] = SELF.R5[Coll[Byte]].get

    // ===== Peform Unstake Tx ===== //

    // Conditions for a valid unstake tx
    val validUnstakeTx: Boolean = {

        // Conditions for a valid input into the unstake tx
        val validUnstakeInput: Boolean = {
            val stakeStateBox: Box = INPUTS(0)
            (stakeStateBox.tokens(0)._1 == StakeStateNFT)
        }

        if (validUnstakeInput) {

            // Unstake Tx Inputs
            val stakeBox: Box = INPUTS(1)

            // Unstake Tx Outputs
            val unstakeAmount: Long = SELF.R4[Coll[Long]].get(0)
            val isEnoughToUnstake: Boolean = (stakeBox.tokens(1)._2 > unstakeAmount)
            val newStakeBoxIsPresent: Int = if (isEnoughToUnstake) 1 else 0  // The new stake box exists if for a partial unstake tx
            val stakeKey: (Coll[Byte], Long) = SELF.tokens(0)
            
            val userWalletBox: Box = OUTPUTS(1)
            val newStakingIncentiveBox: Box = OUTPUTS(2+newStakeBoxIsPresent)
            val txExecutorBox: Box = OUTPUTS(3+newStakeBoxIsPresent)
            val minerFeeBox: Box = OUTPUTS(4+newStakeBoxIsPresent)

            // Check conditions for a valid user wallet output box
            val validUserWalletBox: Boolean = {

                // Check to see if the user wallet box contains the stake key if a partial unstake tx occurs
                val isValidStakeKeyIfPartialUnstake: Boolean = {
                    
                    val isPartialUnstake: Boolean = (newStakeBoxIsPresent == 1)
                    
                    if (isPartialUnstake) {
                        (userWalletBox.tokens(1) == stakeKey)
                    } else {
                        true
                    }

                }

                allOf(Coll(
                    (userWalletBox.propositionBytes == userPropositionBytes),
                    isValidStakeKeyIfPartialUnstake,
                    (userWalletBox.tokens(0)._2 == unstakeAmount)
                ))

            }

            // Check conditions for a valid staking incentive output box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value == ToStakingIncentive),
                    (blake2b256(newStakingIncentiveBox.propositionBytes) == StakingIncentiveContractHash)
                ))
            }

            // Check conditions for a valid tx executor output box
            val validTxExecutorBox: Boolean = (txExecutorBox.value == ExecutorReward)

            // Check conditions for a valid miner fee output box
            val validMinerFeeBox: Boolean = (minerFeeBox.value == MinerFee)

            allOf(Coll(
                validUserWalletBox,
                validNewStakingIncentiveBox,
                validTxExecutorBox,
                validMinerFeeBox,
                (OUTPUTS.size == 5+newStakeBoxIsPresent)
            ))

        } else {
            false
        }

    }

    // ===== Perform Refund Tx ===== //

    // Check conditions for a valid refund tx
    val validRefundTx: Boolean = {

        if (!validUnstakeTx) {
            
            // Conditions for a valid user wallet output box
            val validUserWalletBox: Boolean = {

                val userWalletBox: Box = OUTPUTS(0)

                allOf(Coll(
                    (userWalletBox.value == SELF.value - 1000000),
                    (userWalletBox.propositionBytes == userPropositionBytes),
                    (userWalletBox.tokens == SELF.tokens)  // Check that the user has the stake token returned and the DAO tokens
                ))

            }

            allOf(Coll(
                validUserWalletBox,
                (OUTPUTS.size == 2)
            ))

        } else {
            false
        }
    
    }

    sigmaProp(validUnstakeTx || validRefundTx)

}
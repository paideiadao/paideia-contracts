{

    // ===== Contract Information ===== //
    // Name: addStakeProxy
    // Description: Proxy contract that the user funds to increase their amount of DAO tokens staked, 
    //              it governs the add stake tx and refund tx for the add stake proxy box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Add Stake Proxy Box (SELF) ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Staketime
    //   R5[Coll[Byte]]: User ErgoTree Bytes
    // Tokens:
    //  0:
    //    _1: Stake Key  // NFT used as a key for adding stake as well as unstaking
    //    _2: 1
    //  1:
    //    _1: DAO Token  // Token issued by the DAO, which the user wishes to stake.
    //    _2: > 0 amount that the uers owns and wants to additionally stake.

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

    // ===== Stake Tx ===== //
    // Description: User sends DAO tokens to the stake box and receive a stake key in return, proving they have staked and used for unstaking.
    // Inputs: 
    //   Stake: StakeStateBox, StakeProxyBox
    //   Add Stake: StakeStateBox, StakeBox, AddStakeProxyBox, StakingIncentiveBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: 
    //   Stake: NewStakeStateBox, NewStakeBox, UserWalletBox, NewStakingIncentiveBox, TxOperatorOutputBox
    //   Add Stake: NewStakeStateBox, NewStakeBox, UserWalletBox, NewStakingIncentiveBox, TxOperatorOutputBox

    // ===== Refund Tx ===== //
    // Description: Refund the DAO tokens sent to the add stake proxy contract back to the user's wallet.
    // Inputs: AddStakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: UserWalletBox

    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT: Coll[Byte] =                _stakeStateNFT             // NFT identifying the stake state box
    val StakingIncentiveContractHash: Coll[Byte] = _stakingIncentiveContract  // Blake2b256 hash of the staking incentive contract
    val ToStakingIncentive: Long =                 _toStakingIncentive        // Amount of ERG to insert into the staking incentive output
    val ExecutorReward: Long =                     _executorReward            // Reward for the tx execution bots
    val MinerFee: Long =                           _minerFee                  // Miner fee reward

    // ===== Relevant variables ===== //
    val userPropositionBytes: Coll[Byte] = SELF.R5[Coll[Byte]].get

    // ===== Perform Add Stake Tx ===== //

    // Conditions for a valid add stake tx
    val validAddStakeTx: Boolean = {

        // Conditions for valid inputs to the add stake tx
        val validAddStakeInput: Boolean = {
            val stakeStateBox: Box = INPUTS(0)
            (stakeStateBox.tokens(0)._1 == StakeStateNFT)  // Check that the first input contains the stake state nft
        }

        if (validAddStakeInput) {

            // Add Stake Tx Inputs
            val stakeBox: Box = INPUTS(1)

            // Add Stake Tx Outputs
            val newStakeBox: Box = OUTPUTS(1)
            val userWalletBox: Box = OUTPUTS(2)
            val newStakingIncentiveBox: Box = OUTPUTS(3)
            val txExecutorOutputBox: Box = OUTPUTS(4)
            val minerFeeBox: Box = OUTPUTS(5)
            
            // Relevant variables
            val stakeKey: Coll[Byte] = newStakeBox.R5[Coll[Byte]].get

            // Conditions for a valid new stake box
            val validNewStakeBox: Boolean = {

                // Check that the new stake output box contains the right amount of DAO tokens to stake
                allOf(Coll(
                    (newStakeBox.tokens(1)._1 == SELF.tokens(1)._1),
                    (newStakeBox.tokens(1)._2 == stakeBox.tokens(1)._2 + SELF.tokens(1)._2),
                ))
            
            }

            // Conditions for a valid output user wallet box
            val validUserWalletBox: Boolean = {
                allOf(Coll(
                    (userWalletBox.propositionBytes == userPropositionBytes),
                    (userWalletBox.tokens(0)._1 == stakeKey),  // Check that the user has the stake key in their wallet
                    (userWalletBox.tokens(0)._2 == 1L)
                ))
            }

            // Conditions for a valid output staking incentive box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value == ToStakingIncentive),
                    (blake2b256(newStakingIncentiveBox.propositionBytes) == StakingIncentiveContractHash)
                ))
            }

            // Conditions for a valid tx executor output box (i.e. execution bot box) 
            val validTxExecutorBox: Boolean = {
                (txExecutorOutputBox.value == ExecutorReward)
            }

            val validMinerFeeBox: Boolean = {
                (minerFeeBox.value == MinerFee)
            }

            allOf(Coll(
                validNewStakeBox,
                validUserWalletBox,
                validNewStakingIncentiveBox,
                validTxExecutorBox,
                validMinerFeeBox,
                (OUTPUTS.size == 6)
            ))

        } else {
            false
        }

    }

    // ===== Perform Refund Tx ===== //

    // Conditions for a valid refund tx
    val validRefundTx: Boolean = {

        if (!validAddStakeTx) {
            
            // Conditions for a valid user wallet box
            val validUserWalletBox: Boolean = {

                // Refund Tx Outputs
                val userWalletBox: Boolean = OUTPUTS(0)

                allOf(Coll(
                    (userWalletBox.value == SELF.value - 1000000),             // Miner fee charged for the refund tx
                    (userWalletBox.propositionBytes == userPropositionBytes),  // User PK proposition bytes must match
                    (userWalletBox.tokens == SELF.tokens)                      // All DAO tokens in the this add stake proxy box must be returned to the user
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

    sigmaProp(validAddStakeTx || validRefundTx)

}
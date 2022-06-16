{

    // ===== Contract Information ===== //
    // Name: stakeProxy
    // Description: Proxy contract that the user sends their funds to, which governs the stake and refund tx for the stake proxy box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Stake Proxy Box (SELF) ===== //
    // Registers:
    //   R4[Long]: Stake Time
    //   R5[Coll[Byte]]: User ErgoTree Bytes

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
    // Description: Refund the DAO tokens sent to the stake proxy contract back to the user's wallet.
    // Inputs: StakeProxyBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: UserWalletBox

    // ===== Hard-Coded Constants ===== //
    val StakeStateNFT: Coll[Byte]                = _stakeStateNFT             // NFT identifying the stake state box
    val StakingIncentiveContractHash: Coll[Byte] = _stakingIncentiveContract  // Blake2b256 hash of the staking incentive contract
    val ToStakingIncentive: Long                 = _toStakingIncentive        // Amount of ERG to insert into the staking incentive output
    val ExecutorReward: Long                     = _executorReward            // Reward for the tx execution bot
    val MinerFee: Long                           = _minerFee                  // Miner fee reward

    // ===== Relevant Variables ===== //
    val userPropositionBytes: Coll[Byte] = SELF.R5[Coll[Byte]].get

    // ===== Peform Stake Tx ===== //

    // Conditions for a valid stake tx
    val validStakeTx: Boolean = {

        // Conditions for valid inputs to the stake tx
        val validStakeInput: Boolean = {
            val stakeStateBox: Box = INPUTS(0)
            (stakeStateBox.tokens(0)._1 == StakeStateNFT)  // Check that the first input contains the stake state nft
        }

        if (validStakeInput) {

            // Stake Tx Outputs
            val newStakeBox: Box = OUTPUTS(1)
            val userWalletBox: Box = OUTPUTS(2)
            val newStakingIncentiveBox: Box = OUTPUTS(3)
            val txOperatorOutputBox: Box = OUTPUTS(4)
            val minerFeeBox: Box = OUTPUTS(5)

            // Relevant variables
            val stakeKey: Coll[Byte] = newStakeBox.R5[Coll[Byte]].get
            val stakeTime: Long = SELF.R4[Coll[Long]].get(0)
            
            // Conditions for a valid new stake output box
            val validNewStakeBox: Boolean = {
                allOf(Coll(
                    (newStakeBox.tokens(1) == SELF.tokens(0)),         // Check that the output stake box contains the staked DAO tokens
                    (newStakeBox.R4[Coll[Long]].get(1) == stakeTime),  // Check that the output stake box has the same stake time as a parameter    
                ))
            }

            // Conditions for a valid user wallet output box
            val validUserWalletBox: Boolean = {
                allOf(Coll(
                    (userWalletBox.propositionBytes == userPropositionBytes),
                    (userWalletBox.tokens(0)._1 == stakeKey),  // Check that the user has the stake key in their wallet
                    (userWalletBox.tokens(0)._2 == 1L)
                ))
            }

            // Conditions for a valid staking incentive output box
            val validNewStakingIncentiveBox: Boolean = {
                allOf(Coll(
                    (newStakingIncentiveBox.value == ToStakingIncentive),
                    (blake2b256(newStakingIncentiveBox.propositionBytes) == StakingIncentiveContractHash)
                ))
            }

            // Conditions for a valid tx executor output box (i.e. execution bot box) 
            val validTxExecutorBox: Boolean = {
                (txOperatorOutputBox.value == ExecutorReward)
            }


            // Conditions for a valid miner fee output box
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
    val validRefundTx: Booleam = {

        if (!validStakeTx) {

            // Conditions for a valid user wallet output box
            val validUserWalletBox: Boolean = {
                
                val userWalletBox: Box = OUTPUTS(0)

                allOf(Coll(
                    (userWalletBox.value == SELF.value - 1000000),              // Miner fee charged for the refund tx
                    (userWalletBox.propositionBytes == userPropositionBytes),   // User PK proposition bytes must match the corresponding data stored in the current proxy box
                    (userWalletBox.tokens == SELF.tokens)                       // All DAO tokens in the this stake proxy box must be returned to the user
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

    sigmaProp(validStakeTx || validRefundTx)

}
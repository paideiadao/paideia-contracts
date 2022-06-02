{
    // Stake State
    // Registers:
    // 4:0 Long: Total amount Staked
    // 4:1 Long: Checkpoint
    // 4:2 Long: Stakers
    // 4:3 Long: Last checkpoint timestamp
    // 4:4 Long: Cycle duration
    // Assets:
    // 0: Stake State NFT: 1
    // 1: Stake Token: Stake token to be handed to Stake Boxes

    val blockTime : Long                = CONTEXT.preHeader.timestamp
    val stakedTokenID : Coll[Byte]      = _stakedTokenID
    val stakePoolNFT : Coll[Byte]       = _stakePoolNFT
    val emissionNFT : Coll[Byte]        = _emissionNFT
    val stakeContract : Coll[Byte]      = _stakeContractHash

    val minimumStake : Long             = 1000L

    val stakeStateOutput : Box          = OUTPUTS(0)

    val totalAmountStaked : Long        = SELF.R4[Coll[Long]].get(0)
    val checkpoint : Long               = SELF.R4[Coll[Long]].get(1)
    val stakers : Long                  = SELF.R4[Coll[Long]].get(2)
    val checkpointTimestamp : Long      = SELF.R4[Coll[Long]].get(3)
    val cycleDuration : Long            = SELF.R4[Coll[Long]].get(4)

    val totalAmountStakedOut : Long     = stakeStateOutput.R4[Coll[Long]].get(0)
    val checkpointOut : Long            = stakeStateOutput.R4[Coll[Long]].get(1)
    val stakersOut : Long               = stakeStateOutput.R4[Coll[Long]].get(2)
    val checkpointTimestampOut : Long   = stakeStateOutput.R4[Coll[Long]].get(3)
    val cycleDurationOut : Long         = stakeStateOutput.R4[Coll[Long]].get(4)

    val stakeTokenId : Coll[Byte]       = SELF.tokens(1)._1

    val selfReplication = allOf(Coll(
        stakeStateOutput.propositionBytes == SELF.propositionBytes,
        stakeStateOutput.value == SELF.value,
        stakeStateOutput.tokens(0)._1 == SELF.tokens(0)._1,
        stakeStateOutput.tokens(0)._2 == SELF.tokens(0)._2,
        stakeStateOutput.tokens(1)._1 == stakeTokenId,
        cycleDurationOut == cycleDuration,
        stakeStateOutput.tokens.size == 2
    ))

    val validStakeTxInput : Boolean = OUTPUTS(1).tokens(0)._1 == stakeTokenId

    val stakeTx : Boolean = if (validStakeTxInput) {

        val stakeOutput : Box   = OUTPUTS(1)

        val userOutput : Box    = OUTPUTS(2)

        if (stakeStateOutput.tokens(1)._2 < SELF.tokens(1)._2) {
            // Stake State (SELF), Stake Proxy => Stake State, Stake, Stake Key (User)

            val stakeProxyInput : Box = INPUTS(1)

            allOf(Coll(
                selfReplication,
                // Stake State
                totalAmountStakedOut == totalAmountStaked + stakeOutput.tokens(1)._2,
                checkpointOut == checkpoint,
                stakersOut == stakers+1,
                checkpointTimestampOut == checkpointTimestamp,
                stakeStateOutput.tokens(1)._2 == SELF.tokens(1)._2-1,
                // Stake
                blake2b256(stakeOutput.propositionBytes) == stakeContract,
                stakeOutput.R4[Coll[Long]].get(0) == checkpoint,
                stakeOutput.R4[Coll[Long]].get(1) >= blockTime - 1800000L, //Give half an hour leeway for staking start
                stakeOutput.R5[Coll[Byte]].get == SELF.id,
                stakeOutput.tokens(0)._1 == SELF.tokens(1)._1,
                stakeOutput.tokens(0)._2 == 1L,
                stakeOutput.tokens(1)._1 == stakedTokenID,
                stakeOutput.tokens(1)._2 >= minimumStake,
                //Stake key
                userOutput.propositionBytes == stakeProxyInput.R5[Coll[Byte]].get,
                userOutput.tokens(0)._1 == stakeOutput.R5[Coll[Byte]].get,
                userOutput.tokens(0)._2 == 1L
            ))
        } else {
            // Stake State (SELF), Stake, AddStakeProxy => Stake State, Stake, Stake Key (User)

            val stakeInput : Box            = INPUTS(1)

            val addStakeProxyInput : Box    = INPUTS.getOrElse(2,INPUTS(0))

            allOf(Coll(
                selfReplication,
                // Stake State
                totalAmountStakedOut == totalAmountStaked + stakeOutput.tokens(1)._2 - stakeInput.tokens.getOrElse(1,(Coll[Byte](),0L))._2,
                checkpointOut == checkpoint,
                stakersOut == stakers,
                checkpointTimestampOut == checkpointTimestamp,
                stakeStateOutput.tokens(1)._2 == SELF.tokens(1)._2,
                // // Stake
                stakeOutput.value == stakeInput.value,
                blake2b256(stakeOutput.propositionBytes) == stakeContract,
                blake2b256(stakeInput.propositionBytes) == stakeContract,
                stakeOutput.R4[Coll[Long]].get(0) == checkpoint,
                stakeOutput.R4[Coll[Long]].get == stakeInput.R4[Coll[Long]].get,
                stakeOutput.R5[Coll[Byte]].get == stakeInput.R5[Coll[Byte]].get,
                stakeOutput.tokens(0)._1 == SELF.tokens(1)._1,
                stakeOutput.tokens(0)._2 == 1L,
                stakeOutput.tokens(1)._1 == stakedTokenID,
                stakeOutput.tokens(1)._2 == stakeInput.tokens.getOrElse(1,(Coll[Byte](),0L))._2 + addStakeProxyInput.tokens(1)._2,
                //Stake key
                userOutput.tokens(0)._1 == stakeOutput.R5[Coll[Byte]].get,
                userOutput.tokens(0)._2 == 1L
            ))
        }
    } else {
        false
    }

    val validEmitTxInput : Boolean = if (!validStakeTxInput) INPUTS(1).tokens(0)._1 == stakePoolNFT && INPUTS.size >= 3 else false
    val emitTx : Boolean = if (validEmitTxInput) { // Emit transaction
            // Stake State (SELF), Stake Pool, Emission => Stake State, Stake Pool, Emission
            val emissionInput : Box = INPUTS(2)
            allOf(Coll(
                selfReplication,
                //Emission INPUT
                emissionInput.tokens(0)._1 == emissionNFT,
                emissionInput.R4[Coll[Long]].get(1) == checkpoint - 1L,
                emissionInput.R4[Coll[Long]].get(2) == 0L,
                //Stake State
                checkpointOut == checkpoint + 1L,
                stakersOut == stakers,
                checkpointTimestampOut == checkpointTimestamp + SELF.R4[Coll[Long]].get(4),
                checkpointTimestampOut < blockTime,
                stakeStateOutput.tokens(1)._2 == SELF.tokens(1)._2
            ))
    } else {
        false
    }

    val validUnstakeTxInput : Boolean = if (!(validStakeTxInput || validEmitTxInput)) totalAmountStaked > totalAmountStakedOut && INPUTS.size >= 3 && INPUTS(1).tokens.size > 1 else false
    val unstakeTx : Boolean = if (validUnstakeTxInput) { // Unstake
      // // Stake State (SELF), Stake, UnstakeProxy => Stake State, User Wallet, Stake (optional for partial unstake)
        val stakeInput : Box        = INPUTS(1)
        
        val unstakeProxyInput : Box = INPUTS(2)

        val userOutput : Box        = OUTPUTS(1)

        val unstaked : Long         = totalAmountStaked - totalAmountStakedOut
        val stakeKey : Coll[Byte]   = stakeInput.R5[Coll[Byte]].get
        val remaining : Long        = stakeInput.tokens(1)._2 - unstaked

        allOf(Coll(
            selfReplication,
            unstakeProxyInput.tokens(0)._1 == stakeKey,
            stakeInput.tokens(0)._1 == stakeTokenId,
            stakeInput.R4[Coll[Long]].get(0) == checkpoint,
            //Stake State
            totalAmountStakedOut == totalAmountStaked-unstaked,
            checkpointOut == checkpoint,
            stakersOut == stakers - (if (remaining == 0L) 1L else 0L),
            checkpointTimestampOut == checkpointTimestamp,
            stakeStateOutput.tokens(1)._2 == SELF.tokens(1)._2 + (if (remaining == 0L) 1L else 0L),
            userOutput.tokens(0)._1 == stakeInput.tokens(1)._1,
            userOutput.tokens(0)._2 == unstaked,
            if (remaining > 0L) {
                val stakeOutput : Box = OUTPUTS(2)
                val stakeOutputToken0 : (Coll[Byte],Long) = stakeOutput.tokens.getOrElse(0,(Coll[Byte](),0L))
                val stakeOutputToken1 : (Coll[Byte],Long) = stakeOutput.tokens.getOrElse(1,(Coll[Byte](),0L))
                val stakeOutputR4 : Coll[Long] = if (stakeOutput.R4[Coll[Long]].isDefined) stakeOutput.R4[Coll[Long]].get else Coll(-1L,-1L)
                allOf(Coll(
                    userOutput.tokens.getOrElse(1,(Coll[Byte](),0L))._1 == stakeInput.R5[Coll[Byte]].get,
                    //Stake output
                    stakeOutput.propositionBytes == stakeInput.propositionBytes,
                    stakeOutput.value == stakeInput.value,
                    stakeOutputToken0._1 == stakeInput.tokens(0)._1,
                    stakeOutputToken0._2 == stakeInput.tokens(0)._2,
                    stakeOutputToken1._1 == stakeInput.tokens(1)._1,
                    stakeOutputToken1._2 == remaining,
                    remaining >= minimumStake,
                    stakeOutputR4(0) == stakeInput.R4[Coll[Long]].get(0),
                    stakeOutputR4(1) == stakeInput.R4[Coll[Long]].get(1)
                ))
            } else {
                true
            }
        ))
    } else {
        false
    }
  
    sigmaProp(stakeTx || emitTx || unstakeTx)

}
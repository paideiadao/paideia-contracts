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

  val blockTime = CONTEXT.preHeader.timestamp
  val stakedTokenID = _stakedTokenID
  val stakePoolNFT = _stakePoolNFT
  val emissionNFT = _emissionNFT
  val cycleDuration = SELF.R4[Coll[Long]].get(4)
  val stakeContract = _stakeContractHash
  val minimumStake = 1000L

  val selfReplication = allOf(Coll(
      OUTPUTS(0).propositionBytes == SELF.propositionBytes,
      OUTPUTS(0).value == SELF.value,
      OUTPUTS(0).tokens(0)._1 == SELF.tokens(0)._1,
      OUTPUTS(0).tokens(0)._2 == SELF.tokens(0)._2,
      OUTPUTS(0).tokens(1)._1 == SELF.tokens(1)._1,
      OUTPUTS(0).R4[Coll[Long]].get(4) == cycleDuration,
      OUTPUTS(0).tokens.size == 2
  ))
  if (OUTPUTS(1).tokens(0)._1 == SELF.tokens(1)._1) { // Stake transaction
      if (OUTPUTS(0).tokens(1)._2 < SELF.tokens(1)._2) {
      // // Stake State (SELF), Stake Proxy => Stake State, Stake, Stake Key (User)
        sigmaProp(allOf(Coll(
            selfReplication,
            // Stake State
            OUTPUTS(0).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0) + OUTPUTS(1).tokens(1)._2,
            OUTPUTS(0).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1),
            OUTPUTS(0).R4[Coll[Long]].get(2) == SELF.R4[Coll[Long]].get(2)+1,
            OUTPUTS(0).R4[Coll[Long]].get(3) == SELF.R4[Coll[Long]].get(3),
            OUTPUTS(0).tokens(1)._2 == SELF.tokens(1)._2-1,
            // Stake
            blake2b256(OUTPUTS(1).propositionBytes) == stakeContract,
            OUTPUTS(1).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(1),
            OUTPUTS(1).R4[Coll[Long]].get(1) >= blockTime - 1800000L, //Give half an hour leeway for staking start
            OUTPUTS(1).R5[Coll[Byte]].get == SELF.id,
            OUTPUTS(1).tokens(0)._1 == SELF.tokens(1)._1,
            OUTPUTS(1).tokens(0)._2 == 1L,
            OUTPUTS(1).tokens(1)._1 == stakedTokenID,
            OUTPUTS(1).tokens(1)._2 >= minimumStake,
            //Stake key
            OUTPUTS(2).propositionBytes == INPUTS(1).R5[Coll[Byte]].get,
            OUTPUTS(2).tokens(0)._1 == OUTPUTS(1).R5[Coll[Byte]].get,
            OUTPUTS(2).tokens(0)._2 == 1L
        )))
      } else {
        // Stake State (SELF), Stake, AddStakeProxy => Stake State, Stake, Stake Key (User)
        sigmaProp(allOf(Coll(
            selfReplication,
            // Stake State
            OUTPUTS(0).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0) + OUTPUTS(1).tokens(1)._2 - INPUTS(1).tokens(1)._2,
            OUTPUTS(0).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1),
            OUTPUTS(0).R4[Coll[Long]].get(2) == SELF.R4[Coll[Long]].get(2),
            OUTPUTS(0).R4[Coll[Long]].get(3) == SELF.R4[Coll[Long]].get(3),
            OUTPUTS(0).tokens(1)._2 == SELF.tokens(1)._2,
            // Stake
            blake2b256(OUTPUTS(1).propositionBytes) == stakeContract,
            blake2b256(INPUTS(1).propositionBytes) == stakeContract,
            OUTPUTS(1).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(1),
            OUTPUTS(1).R4[Coll[Long]].get == INPUTS(1).R4[Coll[Long]].get,
            OUTPUTS(1).R5[Coll[Byte]].get == INPUTS(1).R5[Coll[Byte]].get,
            OUTPUTS(1).tokens(0)._1 == SELF.tokens(1)._1,
            OUTPUTS(1).tokens(0)._2 == 1L,
            OUTPUTS(1).tokens(1)._1 == stakedTokenID,
            OUTPUTS(1).tokens(1)._2 == INPUTS(1).tokens(1)._2 + INPUTS(2).tokens(1)._2,
            //Stake key
            OUTPUTS(2).tokens(0)._1 == OUTPUTS(1).R5[Coll[Byte]].get,
            OUTPUTS(2).tokens(0)._2 == 1L
        )))
      }
  } else {
  if (INPUTS(1).tokens(0)._1 == stakePoolNFT && INPUTS.size >= 3) { // Emit transaction
        // Stake State (SELF), Stake Pool, Emission => Stake State, Stake Pool, Emission
        sigmaProp(allOf(Coll(
            selfReplication,
            //Emission INPUT
            INPUTS(2).tokens(0)._1 == emissionNFT,
            INPUTS(2).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1) - 1L,
            INPUTS(2).R4[Coll[Long]].get(2) == 0L,
            //Stake State
            OUTPUTS(0).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1) + 1L,
            OUTPUTS(0).R4[Coll[Long]].get(2) == SELF.R4[Coll[Long]].get(2),
            OUTPUTS(0).R4[Coll[Long]].get(3) == SELF.R4[Coll[Long]].get(3) + SELF.R4[Coll[Long]].get(4),
            OUTPUTS(0).R4[Coll[Long]].get(3) < blockTime,
            OUTPUTS(0).tokens(1)._2 == SELF.tokens(1)._2
        )))
  } else {
  if (SELF.R4[Coll[Long]].get(0) > OUTPUTS(0).R4[Coll[Long]].get(0) && INPUTS.size >= 3 && INPUTS(1).tokens.size > 1) { // Unstake
      // // Stake State (SELF), Stake, UnstakeProxy => Stake State, User Wallet, Stake (optional for partial unstake)
      val unstaked = SELF.R4[Coll[Long]].get(0) - OUTPUTS(0).R4[Coll[Long]].get(0)
      val stakeKey = INPUTS(2).tokens(0)._1 == INPUTS(1).R5[Coll[Byte]].get
      val remaining = INPUTS(1).tokens(1)._2 - unstaked

      sigmaProp(allOf(Coll(
          selfReplication,
          stakeKey,
          INPUTS(1).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(1),
          //Stake State
          OUTPUTS(0).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0)-unstaked,
          OUTPUTS(0).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1),
          OUTPUTS(0).R4[Coll[Long]].get(2) == SELF.R4[Coll[Long]].get(2) - (if (remaining == 0L) 1L else 0L),
          OUTPUTS(0).R4[Coll[Long]].get(3) == SELF.R4[Coll[Long]].get(3),
          OUTPUTS(0).tokens(1)._2 == SELF.tokens(1)._2 + (if (remaining == 0L) 1L else 0L),
          OUTPUTS(1).tokens(0)._1 == INPUTS(1).tokens(1)._1,
          OUTPUTS(1).tokens(0)._2 == unstaked,
          if (remaining > 0L) allOf(Coll(
            OUTPUTS(1).tokens(1)._1 == INPUTS(1).R5[Coll[Byte]].get,
            //Stake output
            OUTPUTS(2).value == INPUTS(1).value,
            OUTPUTS(2).tokens(0)._1 == INPUTS(1).tokens(0)._1,
            OUTPUTS(2).tokens(0)._2 == INPUTS(1).tokens(0)._2,
            OUTPUTS(2).tokens(1)._1 == INPUTS(1).tokens(1)._1,
            OUTPUTS(2).tokens(1)._2 == remaining,
            remaining >= minimumStake,
            OUTPUTS(2).R4[Coll[Long]].get(0) == INPUTS(1).R4[Coll[Long]].get(0),
            OUTPUTS(2).R4[Coll[Long]].get(1) == INPUTS(1).R4[Coll[Long]].get(1)
          ))
          else true
      )))
  } else {
      sigmaProp(false)
  }
  }
  }
}
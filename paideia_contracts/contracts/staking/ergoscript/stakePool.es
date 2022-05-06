{
    // Stake Pool
    // Registers:
    // 4:0 Long: Emission amount per cycle
    // Assets:
    // 0: Stake Pool NFT
    // 1: Remaining Staked Tokens for future distribution (ErgoPad)

    val stakeStateNFT = _stakeStateNFT
    val stakeStateInput = INPUTS(0).tokens(0)._1 == stakeStateNFT
    if (stakeStateInput && INPUTS(1).id == SELF.id) { // Emit transaction
        val dust = (if (INPUTS(2).tokens.size >= 2) INPUTS(2).tokens(1)._2 else 0L)
        val remainingAndDust = SELF.tokens(1)._2 + dust
        val tokensRemaining = if (remainingAndDust > SELF.R4[Coll[Long]].get(0))
                                OUTPUTS(1).tokens(1)._1 == SELF.tokens(1)._1 &&
                                OUTPUTS(1).tokens(1)._2 == remainingAndDust - SELF.R4[Coll[Long]].get(0)
                            else
                                OUTPUTS(1).tokens.size == 1
        sigmaProp(allOf(Coll(
            //Stake State, Stake Pool (self), Emission => Stake State, Stake Pool, Emission
            OUTPUTS(1).propositionBytes == SELF.propositionBytes,
            OUTPUTS(1).tokens(0)._1 == SELF.tokens(0)._1,
            tokensRemaining,
            OUTPUTS(1).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0),
            OUTPUTS(0).R4[Coll[Long]].get(0) == INPUTS(0).R4[Coll[Long]].get(0) + SELF.R4[Coll[Long]].get(0) - dust
        )))
    } else {
        sigmaProp(false)
    }
}
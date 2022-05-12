{
    // Stake Pool
    // Registers:
    // 4:0 Long: Emission amount per cycle
    // 5: Coll[Byte]: Stake pool key
    // Assets:
    // 0: Stake Pool NFT
    // 1: Remaining Staked Tokens for future distribution (ErgoPad)

    val stakeStateNFT = _stakeStateNFT
    val stakeStateInput = INPUTS(0).tokens(0)._1 == stakeStateNFT
    val emissionFeeAddress = _emissionFeeAddress
    
    if (stakeStateInput && INPUTS(1).id == SELF.id) { // Emit transaction
        val dust = (if (INPUTS(2).tokens.size >= 2) INPUTS(2).tokens(1)._2 else 0L)
        val remainingAndDust = SELF.tokens(1)._2 + dust
        val tokensRemaining = if (remainingAndDust > SELF.R4[Coll[Long]].get(0))
                                OUTPUTS(1).tokens(1)._1 == SELF.tokens(1)._1 &&
                                OUTPUTS(1).tokens(1)._2 == remainingAndDust - SELF.R4[Coll[Long]].get(0)
                            else
                                OUTPUTS(1).tokens.size == 1
        sigmaProp(allOf(Coll(
            //Stake State, Stake Pool (self), Emission => Stake State, Stake Pool, Emission, EmissionFee
            OUTPUTS(1).propositionBytes == SELF.propositionBytes,
            OUTPUTS(1).tokens(0)._1 == SELF.tokens(0)._1,
            tokensRemaining,
            OUTPUTS(1).R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0),
            OUTPUTS(0).R4[Coll[Long]].get(0) == INPUTS(0).R4[Coll[Long]].get(0) + (SELF.R4[Coll[Long]].get(0)-SELF.R4[Coll[Long]].get(0) / 100L) - dust,
            if (OUTPUTS(1).tokens.size > 1) {
                allOf(Coll(
                    OUTPUTS(3).propositionBytes == emissionFeeAddress,
                    OUTPUTS(3).value == 1000000,
                    OUTPUTS(3).tokens(0)._1 == SELF.tokens(1)._1,
                    OUTPUTS(3).tokens(0)._2 == SELF.R4[Coll[Long]].get(0) / 100L
                ))
            } else true
        )))
    } else {
    if (INPUTS(0).id == SELF.id) { //Remove funds
        sigmaProp(OUTPUTS(0).tokens(0)._1 == SELF.R5[Coll[Byte]].get)
    } else {
        sigmaProp(false)
    }
    }
}
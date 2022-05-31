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

    val emissionAmount : Long = SELF.R4[Coll[Long]].get(0)
    
    val emitTx : Boolean = if (stakeStateInput && INPUTS(1).id == SELF.id) { // Emit transaction

        val emissionInput : Box = INPUTS(2)

        val stakeStateOutput : Box = OUTPUTS(0)

        val stakePoolOutput : Box = OUTPUTS(1)

        val emissionOutput : Box = OUTPUTS(2)

        val feeOutput : Box = OUTPUTS(3)

        val dust : Long = (if (INPUTS(2).tokens.size >= 2) INPUTS(2).tokens(1)._2 else 0L)

        val remainingAndDust : Long = SELF.tokens(1)._2 + dust

        val tokensRemaining : Long = if (remainingAndDust > emissionAmount)
                                        stakePoolOutput.tokens(1)._1 == SELF.tokens(1)._1 &&
                                        stakePoolOutput.tokens(1)._2 == remainingAndDust - emissionAmount
                                    else
                                        stakePoolOutput.tokens.size == 1

        val totalAmountStaked : Long = INPUTS(0).R4[Coll[Long]].get(0)

        val feeAmount : Long = emissionAmount / 100L
                            
        allOf(Coll(
            //Stake State, Stake Pool (self), Emission => Stake State, Stake Pool, Emission, EmissionFee
            stakePoolOutput.propositionBytes == SELF.propositionBytes,
            stakePoolOutput.tokens(0)._1 == SELF.tokens(0)._1,
            tokensRemaining,
            stakePoolOutput.R4[Coll[Long]].get == SELF.R4[Coll[Long]].get,
            stakeStateOutput.R4[Coll[Long]].get(0) == totalAmountStaked + (emissionAmount-feeAmount) - dust,
            if (stakePoolOutput.tokens.size > 1) {
                allOf(Coll(
                    feeOutput.propositionBytes == emissionFeeAddress,
                    feeOutput.value == 1000000,
                    feeOutput.tokens(0)._1 == SELF.tokens(1)._1,
                    feeOutput.tokens(0)._2 == feeAmount
                ))
            } else true
        ))
    } else {
        false
    }

    val removeFundsTx : Boolean = if (INPUTS(0).id == SELF.id) { //Remove funds
        OUTPUTS(0).tokens(0)._1 == SELF.R5[Coll[Byte]].get
    } else {
        false
    }
    
    sigmaProp(emitTx || removeFundsTx)
}
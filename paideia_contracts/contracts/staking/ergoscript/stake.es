{
    // Stake
    // Registers:
    // 4:0 Long: Checkpoint
    // 4:1 Long: Stake time
    // 5: Coll[Byte]: Stake Key ID to be used for unstaking
    // Assets:
    // 0: Stake Token: 1 token to prove this is a legit stake box
    // 1: Staked Token (ErgoPad): The tokens staked by the user

    val stakeStateNFT = _stakeStateNFT
    val emissionNFT = _emissionNFT
    val stakeStateInput = INPUTS(0).tokens(0)._1 == stakeStateNFT

    if (INPUTS(0).tokens(0)._1 == emissionNFT) { // Compound transaction
        // Emission, Stake*N (SELF) => Emission, Stake * N
        val boxIndex = INPUTS.indexOf(SELF,1)
        val selfReplication = OUTPUTS(boxIndex)
        sigmaProp(allOf(Coll(
            selfReplication.value == SELF.value,
            selfReplication.propositionBytes == SELF.propositionBytes,
            selfReplication.R4[Coll[Long]].get(0) == SELF.R4[Coll[Long]].get(0) + 1,
            selfReplication.R5[Coll[Byte]].get == SELF.R5[Coll[Byte]].get,
            selfReplication.R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(1),
            selfReplication.tokens(0)._1 == SELF.tokens(0)._1,
            selfReplication.tokens(0)._2 == SELF.tokens(0)._2,
            selfReplication.tokens(1)._1 == SELF.tokens(1)._1,
            selfReplication.tokens(1)._2 == SELF.tokens(1)._2 + (INPUTS(0).R4[Coll[Long]].get(3).toBigInt * SELF.tokens(1)._2.toBigInt / INPUTS(0).R4[Coll[Long]].get(0))
        )))
    } else {
    if (INPUTS(1).id == SELF.id) { // Unstake
        if (OUTPUTS(0).R4[Coll[Long]].get(0) < INPUTS(0).R4[Coll[Long]].get(0)) { //Unstake
            val selfReplication = if (OUTPUTS(2).propositionBytes == SELF.propositionBytes)
                                    if (OUTPUTS(2).R5[Coll[Byte]].isDefined)
                                    OUTPUTS(2).R5[Coll[Byte]].get == SELF.R5[Coll[Byte]].get &&
                                    OUTPUTS(1).tokens(1)._1 == INPUTS(1).R5[Coll[Byte]].get
                                    else
                                    false
                                else true
            sigmaProp(stakeStateInput && selfReplication) //Stake state handles logic here to minimize stake box size
        } else { // Add stake
            sigmaProp(stakeStateInput)
        }
    } else {
        sigmaProp(false)
    }
    }
}
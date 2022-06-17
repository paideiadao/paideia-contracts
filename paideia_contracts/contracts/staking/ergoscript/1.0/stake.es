{
    // Stake
    // Registers:
    // 4:0 Long: Checkpoint
    // 4:1 Long: Stake time
    // 5: Coll[Byte]: Stake Key ID to be used for unstaking
    // Assets:
    // 0: Stake Token: 1 token to prove this is a legit stake box
    // 1: Staked Token (ErgoPad): The tokens staked by the user

    val stakeStateNFT : Coll[Byte] = _stakeStateNFT
    val emissionNFT : Coll[Byte] = _emissionNFT
    val stakeStateInput : Boolean = INPUTS(0).tokens(0)._1 == stakeStateNFT

    val checkpoint : Long = SELF.R4[Coll[Long]].get(0)
    val stakeTime : Long = SELF.R4[Coll[Long]].get(1)

    val stakeKey : Coll[Byte] = SELF.R5[Coll[Byte]].get

    val validCompoundTxInput : Boolean = INPUTS(0).tokens(0)._1 == emissionNFT

    val compoundTx : Boolean = if (validCompoundTxInput) { // Compound transaction
        // Emission, Stake*N (SELF) => Emission, Stake * N
        val boxIndex : Long = INPUTS.indexOf(SELF,1)
        val selfReplication : Box = OUTPUTS(boxIndex)
        val emissionInput : Box = INPUTS(0)
        val emissionAmount : BigInt = emissionInput.R4[Coll[Long]].get(3).toBigInt
        val totalAmountStaked : Long = emissionInput.R4[Coll[Long]].get(0)
        val staked : BigInt = SELF.tokens(1)._2.toBigInt
        val reward : Long = emissionAmount * staked / totalAmountStaked
        allOf(Coll(
            selfReplication.value == SELF.value,
            selfReplication.propositionBytes == SELF.propositionBytes,
            selfReplication.R4[Coll[Long]].get(0) == checkpoint + 1,
            selfReplication.R5[Coll[Byte]].get == stakeKey,
            selfReplication.R4[Coll[Long]].get(1) == stakeTime,
            selfReplication.tokens(0)._1 == SELF.tokens(0)._1,
            selfReplication.tokens(0)._2 == SELF.tokens(0)._2,
            selfReplication.tokens(1)._1 == SELF.tokens(1)._1,
            selfReplication.tokens(1)._2 == SELF.tokens(1)._2 + reward
        ))
    } else {
        false
    }

    val validUnstakeTxInput : Boolean = if (!validCompoundTxInput) INPUTS(1).id == SELF.id && OUTPUTS(0).R4[Coll[Long]].get(0) < INPUTS(0).R4[Coll[Long]].get(0) else false

    val unstakeTx : Boolean = if (validUnstakeTxInput) { // Unstake

        val userOutput : Box = OUTPUTS(1)

        val optionalStakeOutput : Box = OUTPUTS(2)

        val selfReplication = if (optionalStakeOutput.propositionBytes == SELF.propositionBytes)
                                    if (optionalStakeOutput.R5[Coll[Byte]].isDefined)
                                        optionalStakeOutput.R5[Coll[Byte]].get == stakeKey &&
                                        userOutput.tokens(1)._1 == SELF.R5[Coll[Byte]].get
                                    else
                                        false
                                else true
        stakeStateInput && selfReplication //Stake state handles logic here to minimize stake box size
    } else {
        false
    }

    val validAddStakeTxInput : Boolean = if (!(validUnstakeTxInput || validCompoundTxInput)) INPUTS(1).id == SELF.id else false

    val addStakeTx : Boolean = if (validAddStakeTxInput) stakeStateInput else false
    
    sigmaProp(compoundTx || unstakeTx || addStakeTx)
}
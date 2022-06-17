{
    //Registers:
    //4: 0: amountToUnstake
    //5: user ergo tree
    //assets:
    //stake key

    val stakeStateNFT : Coll[Byte] = _stakeStateNFT
    val stakingIncentiveContract : Coll[Byte] = _stakingIncentiveContract
    val toStakingIncentive : Long = _toStakingIncentive
    val executorReward : Long = _executorReward
    val minerFee : Long = _minerFee

    val userPropositionBytes : Coll[Byte] = SELF.R5[Coll[Byte]].get

    val validUnstakeTxInput : Boolean = INPUTS(0).tokens(0)._1 == stakeStateNFT

    val unstakeTx : Boolean = if (validUnstakeTxInput) {
        val stakeBoxOutput : Int = if (INPUTS(1).tokens(1)._2 > SELF.R4[Coll[Long]].get(0)) 1 else 0

        val stakeKey : (Coll[Byte],Long) = SELF.tokens(0)

        val userOutput : Box = OUTPUTS(1)

        val incentiveOutput : Box = OUTPUTS(2+stakeBoxOutput)

        val txOperatorOutput : Box = OUTPUTS(3+stakeBoxOutput)

        val minerOutput : Box = OUTPUTS(4+stakeBoxOutput)

        val amountToUnstake : Long = SELF.R4[Coll[Long]].get(0)

        allOf(Coll(
            userOutput.propositionBytes == userPropositionBytes,
            if (stakeBoxOutput == 1) userOutput.tokens(1) == stakeKey else true,
            userOutput.tokens(0)._2 == amountToUnstake,
            blake2b256(incentiveOutput.propositionBytes) == stakingIncentiveContract,
            incentiveOutput.value == toStakingIncentive,
            txOperatorOutput.value == executorReward,
            minerOutput.value == minerFee,
            OUTPUTS.size == 5+stakeBoxOutput
        ))
    } else {
        false
    }

    val refundTx : Boolean = if (!unstakeTx) {
        val userOutput : Box = OUTPUTS(0)
        allOf(Coll(
            userOutput.propositionBytes == userPropositionBytes,
            userOutput.value == SELF.value - 1000000,
            userOutput.tokens == SELF.tokens,
            OUTPUTS.size == 2
        ))
    } else {
        false
    }

    sigmaProp(unstakeTx || refundTx)
}
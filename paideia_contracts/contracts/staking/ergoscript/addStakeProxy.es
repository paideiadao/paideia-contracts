{
    //Registers:
    //4: 0: stakeTime
    //5: user ergo tree
    //assets:
    //stake key
    //tokens to be staked

    val stakeStateNFT : Coll[Byte] = _stakeStateNFT
    val stakingIncentiveContract : Coll[Byte] = _stakingIncentiveContract
    val toStakingIncentive : Long = _toStakingIncentive
    val executorReward : Long = _executorReward
    val minerFee : Long = _minerFee

    val userPropositionBytes : Coll[Byte] = SELF.R5[Coll[Byte]].get

    val addStakeTx : Boolean = {

        val validAddStakeTxInput : Boolean = INPUTS(0).tokens(0)._1 == stakeStateNFT

        if (validAddStakeTxInput) {
            val stakeInput : Box = INPUTS(1)
            val stakeOutput : Box = OUTPUTS(1)
            val userOutput : Box = OUTPUTS(2)
            val incentiveOutput : Box = OUTPUTS(3)
            val txExecutorOutput : Box = OUTPUTS(4)
            val minerOutput : Box = OUTPUTS(5)
            val stakeKey : Coll[Byte] = stakeOutput.R5[Coll[Byte]].get
         
            allOf(Coll(
                stakeOutput.tokens(1)._2 == stakeInput.tokens(1)._2 + SELF.tokens(1)._2,
                stakeOutput.tokens(1)._1 == SELF.tokens(1)._1,
                //Stake key
                userOutput.propositionBytes == userPropositionBytes,
                userOutput.tokens(0)._1 == stakeKey,
                userOutput.tokens(0)._2 == 1L,
                blake2b256(incentiveOutput.propositionBytes) == stakingIncentiveContract,
                incentiveOutput.value == toStakingIncentive,
                txExecutorOutput.value == executorReward,
                minerOutput.value == minerFee,
                OUTPUTS.size == 6
            ))
        } else {
            false
        }
    }

    val refundTx : Boolean = {
        val userOutput : Box = OUTPUTS(0)

        allOf(Coll(
            userOutput.propositionBytes == userPropositionBytes,
            userOutput.value == SELF.value - 1000000,
            userOutput.tokens == SELF.tokens,
            OUTPUTS.size == 2
        ))
    }

    sigmaProp(addStakeTx || refundTx)
}
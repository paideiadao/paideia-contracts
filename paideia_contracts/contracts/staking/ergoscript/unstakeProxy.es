{
    //Registers:
    //4: 0: amountToUnstake
    //5: user ergo tree
    //assets:
    //stake key

    val stakeStateNFT = _stakeStateNFT
    val stakingIncentiveContract = _stakingIncentiveContract
    val toStakingIncentive = _toStakingIncentive
    val executorReward = _executorReward
    val minerFee = _minerFee

    if (INPUTS(0).tokens(0)._1 == stakeStateNFT) {
        val stakeBoxOutput = if (INPUTS(1).tokens(1)._2 > SELF.R4[Coll[Long]].get(0)) 1 else 0
        sigmaProp(
            allOf(Coll(
                OUTPUTS(1).propositionBytes == SELF.R5[Coll[Byte]].get,
                if (stakeBoxOutput == 1) OUTPUTS(1).tokens(1) == SELF.tokens(0) else true,
                OUTPUTS(1).tokens(0)._2 == SELF.R4[Coll[Long]].get(0),
                blake2b256(OUTPUTS(2+stakeBoxOutput).propositionBytes) == stakingIncentiveContract,
                OUTPUTS(2+stakeBoxOutput).value == toStakingIncentive,
                OUTPUTS(3+stakeBoxOutput).value == executorReward,
                OUTPUTS(4+stakeBoxOutput).value == minerFee,
                OUTPUTS.size == 5+stakeBoxOutput
            ))
        )
    } else {
        sigmaProp(
            allOf(Coll(
                OUTPUTS(0).propositionBytes == SELF.R5[Coll[Byte]].get,
                OUTPUTS(0).value == SELF.value - 1000000,
                OUTPUTS(0).tokens == SELF.tokens,
                OUTPUTS.size == 2
            ))
        )
    }
}
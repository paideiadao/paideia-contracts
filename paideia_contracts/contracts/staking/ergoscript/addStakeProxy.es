{
    //Registers:
    //4: 0: stakeTime
    //5: user ergo tree
    //assets:
    //stake key
    //tokens to be staked

    val stakeStateNFT = _stakeStateNFT
    val stakingIncentiveContract = _stakingIncentiveContract
    val toStakingIncentive = _toStakingIncentive
    val executorReward = _executorReward
    val minerFee = _minerFee

    if (INPUTS(0).tokens(0)._1 == stakeStateNFT) {
        sigmaProp(
            allOf(Coll(
                OUTPUTS(1).tokens(1)._2 == INPUTS(1).tokens(1)._2 + SELF.tokens(1)._2,
                OUTPUTS(1).tokens(1)._1 == SELF.tokens(1)._1,
                //Stake key
                OUTPUTS(2).propositionBytes == SELF.R5[Coll[Byte]].get,
                OUTPUTS(2).tokens(0)._1 == OUTPUTS(1).R5[Coll[Byte]].get,
                OUTPUTS(2).tokens(0)._2 == 1L,
                blake2b256(OUTPUTS(3).propositionBytes) == stakingIncentiveContract,
                OUTPUTS(3).value == toStakingIncentive,
                OUTPUTS(4).value == executorReward,
                OUTPUTS(5).value == minerFee,
                OUTPUTS.size == 6
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
{
    //Registers:
    //4: 0: stakeTime
    //5: user ergo tree

    val stakeStateNFT = _stakeStateNFT
    val stakingIncentiveContract = _stakingIncentiveContract

    if (SELF.value > ) {
        sigmaProp(
            allOf(Coll(
                INPUTS(0).tokens(0)._1 == stakeStateNFT,
                OUTPUTS(1).tokens(1) == SELF.tokens(0),
                OUTPUTS(1).R4[Coll[Long]].get(1) == SELF.R4[Coll[Long]].get(0),
                //Stake key
                OUTPUTS(2).propositionBytes == INPUTS(1).propositionBytes,
                OUTPUTS(2).tokens(0)._1 == OUTPUTS(1).R5[Coll[Byte]].get,
                OUTPUTS(2).tokens(0)._2 == 1L,
                blake2b256(OUTPUTS(3).propositionBytes) == stakingIncentiveContract,
                OUTPUTS(3).value == 100000000,
                OUTPUTS(4).value == 2000000,
                OUTPUTS(5).value == 2000000,
                OUTPUTS.size == 6
            ))
        )
    }
}
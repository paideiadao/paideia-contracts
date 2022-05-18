{
    val emissionNFT = _emissionNFT
    val stakeStateNFT = _stakeStateNFT
    val stakeTokenID = _stakeTokenID
    val stakePoolKey = _stakePoolKey
    val dustCollectionReward = _dustCollectionReward
    val dustCollectionMinerFee = _dustCollectionMinerFee
    val emitReward = _emitReward
    val emitMinerFee = _emitMinerFee
    val baseCompoundReward = _baseCompoundReward
    val baseCompoundMinerFee = _baseCompoundMinerFee
    val variableCompoundReward = _variableCompoundReward
    val variableCompoundMinerFee = _variableCompoundMinerFee

    //Dust consolidation tx
    if (OUTPUTS.size == 3)
    {
        val dustBoxes = INPUTS.filter({(box: Box) => box.propositionBytes == SELF.propositionBytes}).size
        val reward = dustCollectionReward * dustBoxes
        sigmaProp(allOf(Coll(
            OUTPUTS(0).propositionBytes == SELF.propositionBytes,
            OUTPUTS(0).value > SELF.value,
            SELF.value <= 100000000,
            OUTPUTS(1).value == reward,
            OUTPUTS(2).value == dustCollectionMinerFee
        )))
    } else {
        //Emit transaction
        if (INPUTS(0).tokens(0)._1 == stakeStateNFT && INPUTS(2).tokens(0)._1 == emissionNFT)
        {
            sigmaProp(allOf(Coll(
                INPUTS(INPUTS.size-1).id == SELF.id,
                OUTPUTS(4).propositionBytes == SELF.propositionBytes,
                OUTPUTS(4).value >= SELF.value - emitReward - emitMinerFee - 1000000,
                OUTPUTS(5).value == emitReward,
                OUTPUTS(6).value == emitMinerFee
            )))
        }
        else
        {
            //Compound transaction
            if (INPUTS(0).tokens(0)._1 == emissionNFT)
            {
                val stakeBoxes = INPUTS.filter({(box: Box) => if (box.tokens.size > 0) box.tokens(0)._1 == stakeTokenID && box.R4[Coll[Long]].get(0) == INPUTS(0).R4[Coll[Long]].get(1) else false}).size
                val reward = baseCompoundReward + variableCompoundReward * stakeBoxes
                val minerFee = baseCompoundMinerFee + variableCompoundMinerFee * stakeBoxes
                sigmaProp(allOf(Coll(
                    INPUTS(INPUTS.size-1).id == SELF.id,
                    OUTPUTS(INPUTS.size-1).propositionBytes == SELF.propositionBytes,
                    OUTPUTS(INPUTS.size-1).value >= SELF.value - reward - minerFee,
                    OUTPUTS(INPUTS.size).value == reward,
                    OUTPUTS(INPUTS.size+1).value == minerFee,
                    INPUTS.size == stakeBoxes + 2
                )))
            }
            else
            {
                sigmaProp(OUTPUTS(0).tokens(0)._1 == stakePoolKey)
            }
        }
    }
}
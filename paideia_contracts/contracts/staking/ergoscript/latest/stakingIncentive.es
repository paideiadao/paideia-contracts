{
    val emissionNFT : Coll[Byte]        = _emissionNFT
    val stakeStateNFT : Coll[Byte]      = _stakeStateNFT
    val stakeTokenID : Coll[Byte]       = _stakeTokenID
    val stakePoolKey : Coll[Byte]       = _stakePoolKey
    val dustCollectionReward : Long     = _dustCollectionReward
    val dustCollectionMinerFee : Long   = _dustCollectionMinerFee
    val emitReward : Long               = _emitReward
    val emitMinerFee : Long             = _emitMinerFee
    val baseCompoundReward : Long       = _baseCompoundReward
    val baseCompoundMinerFee : Long     = _baseCompoundMinerFee
    val variableCompoundReward : Long   = _variableCompoundReward
    val variableCompoundMinerFee : Long = _variableCompoundMinerFee

    val validConsolidateTxInput : Boolean = OUTPUTS.size == 3
    
    val consolidateTx : Boolean = if (validConsolidateTxInput)
    {
        val dustBoxes : Long = INPUTS.filter({(box: Box) => box.propositionBytes == SELF.propositionBytes}).size
        val reward : Long = dustCollectionReward * dustBoxes
        val incentiveOutput : Box = OUTPUTS(0)
        val txOperatorOutput : Box = OUTPUTS(1)
        val minerOutput : Box = OUTPUTS(2)
        allOf(Coll(
            incentiveOutput.propositionBytes == SELF.propositionBytes,
            incentiveOutput.value > SELF.value,
            SELF.value <= 100000000,
            txOperatorOutput.value == reward,
            minerOutput.value == dustCollectionMinerFee
        ))
    } else {
        false
    }
    
    val validEmitTxInput : Boolean = if (!validConsolidateTxInput) INPUTS(0).tokens.getOrElse(0,(Coll[Byte](),0L))._1 == stakeStateNFT && INPUTS(2).tokens.getOrElse(0,(Coll[Byte](),0L))._1 == emissionNFT else false
    val emitTx : Boolean = if (validEmitTxInput)
    {
        val incentiveOutput : Box = OUTPUTS(4)
        val txOperatorOutput : Box = OUTPUTS(5)
        val minerOutput : Box = OUTPUTS(6)
        allOf(Coll(
            INPUTS(INPUTS.size-1).id == SELF.id,
            incentiveOutput.propositionBytes == SELF.propositionBytes,
            incentiveOutput.value >= SELF.value - emitReward - emitMinerFee - 1000000,
            txOperatorOutput.value == emitReward,
            minerOutput.value == emitMinerFee
        ))
    }
    else
    {
        false
    }

    val validCompoundTxInput : Boolean = if (!(validConsolidateTxInput || validEmitTxInput)) INPUTS(0).tokens.getOrElse(0,(Coll[Byte](),0L))._1 == emissionNFT else false
            //Compound transaction
    val compoundTx : Boolean = if (validCompoundTxInput)
    {
        val stakeBoxes : Long = INPUTS.filter({(box: Box) => if (box.tokens.size > 0) box.tokens(0)._1 == stakeTokenID && box.R4[Coll[Long]].get(0) == INPUTS(0).R4[Coll[Long]].get(1) else false}).size
        val reward : Long = baseCompoundReward + variableCompoundReward * stakeBoxes
        val minerFee : Long = baseCompoundMinerFee + variableCompoundMinerFee * stakeBoxes

        val incentiveOutput : Box = OUTPUTS(INPUTS.size-1)
        val txOperatorOutput : Box = OUTPUTS(INPUTS.size)
        val minerOutput : Box = OUTPUTS(INPUTS.size+1)
        allOf(Coll(
            INPUTS(INPUTS.size-1).id == SELF.id,
            incentiveOutput.propositionBytes == SELF.propositionBytes,
            incentiveOutput.value >= SELF.value - reward - minerFee,
            txOperatorOutput.value == reward,
            minerOutput.value == minerFee,
            INPUTS.size == stakeBoxes + 2
        ))
    } else {
        false
    }

    val stakePoolKeyTx : Boolean = if (!(validConsolidateTxInput || validEmitTxInput || validCompoundTxInput)) {
        val stakePoolOutput : (Coll[Byte],Long) = OUTPUTS(0).tokens.getOrElse(0,(Coll[Byte](),0L))
        stakePoolOutput._1 == stakePoolKey
    } else {
        false
    }
     
    sigmaProp(consolidateTx || emitTx || compoundTx || stakePoolKeyTx)
}
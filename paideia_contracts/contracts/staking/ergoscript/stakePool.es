{
     // ===== Contract Information ===== //
    // Name: stakePool
    // Description: Contract that governs the emit and remove funds transactions for the stake pool box.
    // Version: 1.0
    // Authors: Lui, Luca

    // ===== Stake Pool Box (SELF) ===== //
    // Registers:
    //   R4[Long]: Emission Amount
    //   R5[Coll[Byte]]: Stake Pool Key
    // Tokens:
    //   0:
    //     _1: Stake Pool NFT: Identifier for the stake pool box.
    //     _2: Amount: 1
    //   1:
    //     _1: DAO Token ID: Token issued by the DAO for distribution
    //     _2: Amount: <= Total DAO Tokens Amount

    // ===== Stake State Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Total Amount Staked
    //     1: Checkpoint
    //     2: Stakers
    //     3: Last Checkpoint Timestamp
    //     4: Cycle Duration 
    // Tokens:
    //   0: 
    //     _1: Stake State NFT: Identifier for the stake state box.
    //     _2: Amount: 1  
    //   1: 
    //     _1: Stake Token: Token proving that the stake box was created properly.
    //     _2: Amount: <= 1 Billion

    // ===== Emission Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Total Amount Staked
    //     1: Checkpoint
    //     2: Stakers
    //     3: Emission Amount
    // Tokens:
    //   0: 
    //     _1: Emission NFT: Identifier for the emission box.
    //     _2: Amount: 1
    //   1: 
    //     _1: DAO Token ID: Tokens to be emitted by the DAO.
    //     _2: Amount: <= DAO Token Emission Amount

    // ===== Stake Box ===== //
    // Registers:
    //   R4[Coll[Long]]:
    //     0: Checkpoint
    //     1: Staking Time
    //   R5[Coll[Byte]]: Stake Key ID // ID of the stake key used for unstaking.
    // Tokens:
    //   0:
    //     _1: Stake Token: Token proving that the stake box was created properly.
    //     _2: Amount: 1
    //   1:
    //     _1: DAO Token: Token issued by the DAO, which the user wishes to stake.
    //     _2: Amount: > 0

    // ===== Emit Tx ===== //
    // Description: Ran once per day, determining the amount from the stake pool to be withdrawn into a new emission box before being distributed to the stakers.
    // Inputs: StakeStateBox, StakePoolBox, EmissionBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: NewStakeStateBox, NewStakePoolBox, NewEmissionBox

    // ===== Remove Funds Tx ===== //
    // Description: Removing funds from the stake pool box.
    // Inputs: StakePoolBox
    // DataInputs: None
    // Context Extension Variables: None
    // Outputs: 

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
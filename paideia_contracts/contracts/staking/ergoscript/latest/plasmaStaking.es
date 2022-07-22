{
  val stakeState = SELF.R4[AvlTree].get
  val emissionAmount = SELF.R5[Coll[Long]].get(0)
  val emissionDelay = SELF.R5[Coll[Long]].get(1)
  val cycleLength = SELF.R5[Coll[Long]].get(2)
  val nextSnapshot = SELF.R5[Coll[Long]].get(3)
  val stakers = SELF.R5[Coll[Long]].get(4)
  val totalStaked = SELF.R5[Coll[Long]].get(5)
  val snapshots = SELF.R6[Coll[(Long,(Long,AvlTree))]].get

  val STAKE = 0.toByte
  val CHANGE_STAKE = 1.toByte
  val UNSTAKE = 2.toByte
  val SNAPSHOT = 3.toByte
  val COMPOUND = 4.toByte

  val plasmaStakingOutput = OUTPUTS(0)

  val transactionType = getVar[Byte](0).get

  val validTransactionType = transactionType >= 0 && transactionType <= 5

  val validOutput = allOf(
    plasmaStakingOutput.propositionBytes == SELF.propositionBytes,
    plasmaStakingOutput.tokens(0) == SELF.tokens(0),
    plasmaStakingOutput.tokens(1)._1 == SELF.tokens(1)._1
  )

  val validStake = {
    if (transactionType == STAKE) {
      val stakeOperations  = getVar[Coll[(Coll[Byte], Coll[Byte]])](1).get
      val proof   = getVar[Coll[Byte]](2).get

      val userOutput = OUTPUTS(1)

      val stakeAmount = byteArrayToLong(stakeOperations(0)._2.slice(0,8))

      val correctKeyMinted = SELF.id == stakeOperations(0)._1 == userOutput.tokens(0)._1
      val correctAmountMinted = userOutput.tokens(0)._2 == 1

      val tokensStaked = (plasmaStakingOutput.tokens(1)._2 - SELF.tokens(1)._2) == stakeAmount == plasmaStakingOutput.R5[Coll[Long]].get(5) - totalStaked

      val singleStakeOp = stakeOperations.size == 1

      val correctNewState = stakeState.insert(stakeOperations, proof).digest == plasmaStakingOutput.R4[AvlTree].get.digest
      
      allOf(
        correctKeyMinted,
        correctAmountMinted,
        tokensStaked,
        singleStakeOp,
        correctNewState
      )
    } else {
      true
    }
  }

  val validChangeStake = {
    if (transactionType == CHANGE_STAKE) {
      val stakeOperations  = getVar[Coll[(Coll[Byte], Coll[Byte]])](1).get
      val proof   = getVar[Coll[Byte]](2).get

      val userOutput = OUTPUTS(1)

      val keyInOutput = userOutput.tokens(0)._1 == stakeOperations(0)._1

      val newStakeAmount = byteArrayToLong(stakeOperations(0)._2.slice(0,8))

      currentStakeState = stakeState.get(stakeOperations(0)._1, proof)

      val currentStakeAmount = byteArrayToLong(currentStakeState._2.slice(0,8))

      val tokensStaked = (plasmaStakingOutput.tokens(1)._2 - SELF.tokens(1)._2) == newStakeAmount - currentStakeAmount == plasmaStakingOutput.R5[Coll[Long]].get(5) - totalStaked

      val singleStakeOp = stakeOperations.size == 1

      val correctNewState = stakeState.update(stakeOperations, proof).digest == plasmaStakingOutput.R4[AvlTree].get.digest
      
      allOf(
        keyInOutput,
        tokensStaked,
        singleStakeOp,
        correctNewState
      )
    } else {
      true
    }
  }

  val validUnstake = {
    if (transactionType == UNSTAKE) {
      val keys  = getVar[Coll[Coll[Byte]]](1).get
      val proof   = getVar[Coll[Byte]](2).get

      val userInput = INPUTS(1)

      val keyInInput = userInput.tokens(0)._1 == keys(0)

      currentStakeState = stakeState.get(keys(0), proof)

      val currentStakeAmount = byteArrayToLong(currentStakeState._2.slice(0,8))

      val tokensUnstaked = (SELF.tokens(1)._2 - plasmaStakingOutput.tokens(1)._2) == currentStakeAmount == totalStaked - plasmaStakingOutput.R5[Coll[Long]].get(5)

      val singleStakeOp = keys.size == 1

      val correctNewState = stakeState.remove(keys, proof).digest == plasmaStakingOutput.R4[AvlTree].get.digest
      
      allOf(
        keyInInput,
        tokensStaked,
        singleStakeOp,
        correctNewState
      )
    } else {
      true
    }
  }

  val validSnapshot = {
    if (transactionType == SNAPSHOT) {
      val correctSnapshotUpdate = {
        val newSnapshots = plasmaStakingOutput.R6[Coll[(Long,(Long,AvlTree))]].get

        val correctNewSnapshot = allOf(
          newSnapshots(0)._1 == stakers,
          newSnapshots(0)._2._1 == totalStaked,
          newSnapshots(0)._2._2 == stakeState
        )
        
        val correctHistoryShift = if (snapshots.size > 0) 
          {
            allOf(Coll(
              if (snapshots.size >= emissionDelay) snapshots(emissionDelay-1)._1 == 0 else true,
              newSnapshots.slice(1,if (snapshots.size < emissionDelay) snapshots.size else emissionDelay) == snapshots.slice(0,if (snapshots.size < emissionDelay) snapshots.size else emissionDelay)
            ))
          } else {
            true
          }

        val correctSize = newSnapshots.size <= emissionDelay
      }
    } else {
      true
    }
  }

  val validCompound = {
    if (transactionType == COMPOUND) {
      val compoundOperations  = getVar[Coll[(Coll[Byte], Coll[Byte]])](1).get
      val proof   = getVar[Coll[Byte]](2).get
      val snapshotProof   = getVar[Coll[Byte]](3).get

      val keys = compoundOperations.map{(kv: (Coll[Byte], Coll[Byte])) => kv._1}

      val filteredCompoundOperations = compoundOperations.filter{(kv: (Coll[Byte], Coll[Byte])) => byteArrayToLong(kv._2) > 0}

      val currentStakes = stakeState.getMany(keys,proof)

      val snapshotStakes = snapshots(emissionDelay-1)._2._2.getMany(keys,snapshotProof)

      val snapshotStaked = snapshots(emissionDelay-1)._2._1

      val rewards = keys.map{
        (key: Coll[Byte]) =>
          val index = keys.indexOf(key,0)

          if (currentStakes(index).isDefined) {
            val snapshotStake = byteArrayToLong(snapshotStakes(index))
            snapshotStake.toBigInt * emissionAmount.toBigInt / snapshotStaked
          } else {
            0L
          }
      }

      val validCompounds = keys.forall{
        (key: Coll[Byte]) =>
          val index = keys.indexOf(key,0)

          if (currentStakes(index).isDefined) {
            val currentStake = byteArrayToLong(currentStakes(index))
            val newStakeAmount = currentStake + rewards(index)
            
            newStakeAmount == byteArrayToLong(compoundOperations(index)._2)
          } else {
            snapshotStakes(key).isDefined
          }
      }

      val totalRewards = rewards.fold(0L, {(z: Long, reward: Long) => z + reward})

      val correctTotalStaked = totalStaked + totalRewards == plasmaStakingOutput.R5[Coll[Long]].get(5)

      val correctSnapshot = snapshots(emissionDelay-1)._2._2.remove(keys, snapshotProof).digest == plasmaStakingOutput.R6[Coll[(Long,(Long,AvlTree))]].get(emissionDelay-1)._2._2.digest

      val correctStakerCount = snapshots(emissionDelay-1)._1 - keys.size == plasmaStakingOutput.R6[Coll[(Long,(Long,AvlTree))]].get(emissionDelay-1)._1
      
      val correctNewState = stakeState.update(filteredCompoundOperations, proof).digest == plasmaStakingOutput.R4[AvlTree].get.digest
      
      allOf(Coll(
        validCompounds,
        correctTotalStaked,
        correctSnapshot,
        correctNewState
      ))
    } else {
      true
    }
  }

  sigmaProp(
    allOf(Coll(
      validTransactionType,
      validOutput,
      validStake,
      validChangeStake,
      validUnstake,
      validSnapshot,
      validCompound
    ))
  )
}
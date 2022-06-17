# Paideia Staking Protocol

EIP-6 specification for the Paideai staking protocol.

# Stages

1. [Staking Incentive](#stage-staking-incentive)
2. [Stake Proxy](#stage-stake-proxy)
3. [Stake State](#stage-stake-state)
4. [Stake Pool](#stage-stake-pool)
5. [Staking](#stage-stake)
6. [Emission](#stage-emission)
7. [Unstake Proxy](#stage-unstake-proxy)
8. [Add Stake Proxy](#stage-add-stake-proxy)

# Spending Paths

1. [Bootstrap Stake Pool](#action-bootstrap-stake-pool)
2. [Stake](#action-stake)
3. [Emit](#action-emit)
4. [Compound](#action-compound)
5. [Unstake](#action-unstake)
6. [Add Stake](#action-add-stake)
7. [Consolidate](#action-consolidate)
8. [Remove Funds](#action-remove-funds)

---

## Stage: Staking Incentive

Proxy contract that governs the consolidate, emit, compound, and remove funds transactions for the staking incentive box. The staking incentive box pays the transaction execution bots.

### Registers

- None

### Tokens

- None

### Hard-Coded Constants

- EmissionNFT [Coll[Byte]]: Identifier for the emission box.
- StakeStateNFT [Coll[Byte]]: Identifier for the stake state box.
- StakeTokenID [Coll[Byte]]: Token proving that the stake box was created properly.
- StakePoolKey [Coll[Byte]]: Stake pool key used for accesssing the stake pool box funds.
- DustCollection Reward [Long]: Dust consolidation tx reward for the execution bot.
- DustCollection Miner Fee [Long]: Dust consolidation tx miner fee.
- EmitReward [Long]: Emit tx reward for the execution bot. 
- EmitMinerFee [Long]: Emit transaction miner fee
- BaseCompoundReward [Long]: Base compound tx reward for the execution bot.
- BaseCompoundMiner Fee [Long]: Base compound tx miner fee.
- VariableCompoundReward [Long]: Variable compound tx reward for the execution bot.
- VariableCompoundMiner Fee [Long]: Base compound tx miner fee reward.
- StakingIncentiveBoxMaxValue [Long]: Max ERG value the staking incentive box can have.

### Context Extension Variables

- None

### Spending Paths

- [Consolidate](<#action-consolidate>)
- [Emit](<#action-emit>)
- [Compound](<#action-compound>)
- [Remove Funds](<#action-remove-funds>)
  
---

## Stage: Stake Proxy

When a user wants to stake their DAO tokens for the first time, they will send them to this proxy box. The proxy contract will govern the stake and refund txs for the funds in this box. This proxy contract ensures that the user's DAO tokens will be moved to a corresponding stake box or otherwise can be refunded back to them.

### Registers

- R4[Long]: Stake Time
- R5[Coll[Byte]]: User ErgoTree Bytes

### Tokens

- None

### Hard-Coded Constants

- StakeStateNFT Coll[Byte]]: NFT identifying the stake state box
- StakingIncentiveContractHash Coll[Byte]: Blake2b256 hash of the staking incentive contract
- ToStakingIncentive [Long]:  Amount of ERG to insert into the staking incentive output
- ExecutorReward [Long]: Reward for the tx execution bot
- MinerFee: [Long]: Miner fee reward

### Context Extension Variables

- None

### Spending Paths

- [Stake](<#action-stake>)
- [Refund](<#action-refund>) 

---

## Stage: Stake State

Contract that governs the stake (initial stake and add stake), emit, and unstake (full unstake and partial unstake) txs for the stake state box. This box, identified by the *Stake State NFT*, keeps track of the global state of the system. The next emission cycle is initiated by increasing the checkpoint and adding a cycle lenngth to the last checkpoint timestamp.

### Registers

- R4[Coll[Long]]:
  - 0: Total Amount Staked
  - 1: Checkpoint
  - 2: Stakers
  - 3: Last Checkpoint Timestamp
  - 4: Cycle Duration

### Tokens

- 0:
  - _1: Stake State NFT
  - _2: 1

- 1:
  - _1: Stake Token
  - _2: <= 1 Billion

### Hard-Coded Constants

- BlockTime [Long]: Timestamp from the blockchain preheader
- StakedTokenID [Coll[Byte]]: Token identifier for the token distributed by the dao
- StakePoolNFT [Coll[Byte]]: Identifier for the stake pool box
- EmissionNFT [Coll[Byte]]: Identifier for the emission box
- StakeContract [Coll[Byte]]: Hash of the staking contract P2S address
- MinimumStake [Long]: Minimum amount of DAO tokens required for staking 

### Context Extension Variables

- None

### Spending Paths

- [Stake](<#action-stake>)
- [Emit](<#action-emit>)
- [Unstake](<#action-unstake>)
  
---

## Stage: Stake Pool

The stake pool contains all of the DAO tokens needed for the staking protocol. The contract governs the emit and remove funds txs for this box. Emission will require the stake pool to withdraw funds into the emission box for compounding the user stake boxes. If changes to the staking protocol are made, funds can also be withdrawn and transferred to the new system.

### Registers

- R4[Long]: Emission Amount
- R5[Coll[Byte]]: Stake Pool Key

### Tokens

- 0:
  - _1: Stake Pool NFT
  - _2: 1

- 1:
  - _1: DAO Token ID
  - _2: <= Total DAO Tokens Amount

### Hard-Coded Constants

- StakeStateNFT [Coll[Byte]]: NFT identifying the stake state box
- EmissionFeeAddress [Coll[Byte]]: Address where the emission fee is sent

### Context Extension Variables

- None

### Spending Paths

- [Emit](<#action-emit>)
- [Remove Funds](<#action-remove-funds>)
  
---

## Stage: Staking

Contract that governs the compound, unstake, and add stake txs for the stake box. The stake box contains the user's DAO tokens used for staking in the protocol. The user will receive the *Stake Key NFT*, proving they have the rights to the corresponding stake box. The stake state box keeps track of the increased amount of stake boxes and the total amount staked. During the next emission cycle, for compounding, the emission box sends funds to the stake box. 

### Registers

- R4[Coll[Long]]:
  - 0: Total Amount Staked
  - 1: Checkpoint
  - 2: Stakers
  - 3: Last Checkpoint Timestamp
  - 4: Cycle Duration

### Tokens

- 0:
  - _1: Stake Tokens
  - _2: 1

- 1:
  - _1: DAO Token
  - _2: > 0

### Hard-Coded Constants

- StakeStateNFT [Coll[Byte]]: Identifier for the stake state box
- EmissionNFT [Coll[Byte]]: Identifier for the emission box

### Context Extension Variables

- None

### Spending Paths

- [Compoud](<#action-compound>)
  
---

## Stage: Emission

In this stage, the user has already staked their DAO tokens. The next emission snapshot begins, where emission tokens are taken from the stake pool and ready to be distributed to stake holders in their respective stake boxes. The contract governs the emit and compound txs for the emission box.

### Registers

- R4[Coll[Long]]:
  - 0: Total amount staked
  - 1: Checkpoint
  - 2: Stakers
  - 3: Emission amount

### Tokens:

- 0:
  - _1: Emission NFT
  - _2: 1
- 1:
  - _1: DAO Token ID
  - _2: <= DAO Token Emission Amount

### Hard-Coded Constants

- Stake State NFT [Coll[Byte]]: NFT identifying the stake state box.
- Stake Token ID [Coll[Byte]]: Token proving that the stake box was created properly.
- Staked Token ID [Coll[Byte]]: Token identifier for the token distributed by the DAO.

### Context Extension Variables

None

### Spending Paths

- [Emit](#action-emit)
- [Compound](#action-compound)
  
---

## Stage: Unstake Proxy

For whatever reason, the user wishes to withdraw their DAO tokens from the staking protocol. Their stake token is sent to the unstake proxy box and the contract governs the unstake tx and refund tx for the this box. For a full unstake, the stake state box will be updated to account for the reduced amount of stakers and reduced total amount of staked tokens. The user's stake token will also be re-claimed. For a partial unstake, the user will receive their stake token back in thei wallet. The stake state box will account for the reduced total amount of stake, but the total amount of stakers has not changed. In both cases, the user will not have to a pay a penalty for unstaking.

### Registers

- R4[Coll[Long]]:
  - 0: Unstake Amount
- R5[Coll[Byte]]: User ErgoTree Bytes

### Hard-Coded Constants

- StakeStateNFT [Coll[Byte]]: NFT identifying the stake state box
- StakingIncentiveContractHash [Coll[Byte]]: Blake2b256 hash of the staking incentive contract
- ToStakingIncentive [Long]: Amount of ERG to insert into the staking incentive output
- ExecutorReward [Long]: Reward for the tx execution bot
- MinerFee [Long]: Miner fee reward

### Context Extension Variables

- None

### Spending Paths

- [Unstake](<#action-unstake>)
- [Refund](<#action-refund>)
  
---

## Stage: Add Stake Proxy

Proxy contract that the user funds with their DAO tokens and their stake key to increase their amount of DAO tokens staked, it governs the add stake tx and refund tx for the add stake proxy box. The stake state box will be updated to account for the increased total amount of stake in the protocol. The user's stake key will be sent back to them after the add stake or refund txs.

### Registers

- R4[Coll[Long]]:
  - 0: Staketime
- R5[Coll[Byte]]: User ErgoTree Bytes

### Hard-Coded Constants

- StakeStateNFT [Coll[Byte]]: NFT identifying the stake state box
- StakingIncentiveContractHash [Coll[Byte]]: Blake2b256 hash of the staking incentive contract
- ToStakingIncentive [Long]: Amount of ERG to insert into the staking incentive output
- ExecutorReward [Long]: Reward for the tx execution bot
- MinerFee [Long]: Miner fee reward

### Context Extension Variables

  - None

### Spending Paths

- [Add Stake](<#action-add-stake>)
- [Refund](<#action-refund>)
  
---

## Action: Bootstrap Stake Pool

Bootstrapping the stake pool by sending DAO tokens to the stake pool contract.

### Inputs

1. Box with DAO tokens, not held in the stake pool contract.

### Outputs

1. The stake pool box holding the DAO tokens.

---

## Action: Stake

The user wants to stake for the first time in the staking protocol and sends their desired amount of DAO tokens to the stake proxy contract. In return, they receive a stake token as proof of their participation within the staking protocol. The key is used to unstake or add stake later on.

### Data-Inputs

   - None

### Inputs

  0. Stake State Box
  1. Stake Proxy Box 

### Outputs

  0. New Stake State Box
  1. New Stake Box
  2. User Wallet Box
  3. New Staking Incentive Box
  4. Tx Operator Output Box

### Action Conditions

#### Condition 1: Valid Initial Stake
  1. Stake State Contract:
     1. The output stake box contains the stake token id.

#### Condition 2: Valid Stake Input
  1. Stake Proxy Contract:
     1. The first input must contain the Stake State NFT (i.e. it must be the stake state box).

#### Condition 3: Valid New Stake State Box
  1. Stake State Contract:
     1. Valid Self Replication
        1. The box retains the same amount of ERG.
        2. The contract guarding the box remains the same.
        3. The box retains the same amount of tokens - stake state NFT and stake token - and the same amount for each.
        4. The emission cycle duration remains constant.
     2. The total amount staked must increase by the amount provided from the user in the stake proxy box.
     3. The staking checkpoint remains constants.
     4. The amount of stakers increases by one.
     5. The emission checkpoint timestamp remains constant.
     6. The amount of stake tokens decreases by one, since it is sent to the user as proof of stake...

#### Condition 4: Valid New Stake Box
  1. Stake State Contract:
     1. The blake2b256 hash of the stake box contract must be the same hard-coded value in the stake state contract.
     2. The stake box stores the checkpoint in R4.
     3. The staking time stored in R5 must be greater than the current block time minus 1.8 million.
     4. The stake key id - the box id of the stake state box - is stored in R5 of the stake box.
     5. The new stake box must contain the stake token NFT.
     6. The new stake box must contain at least the hard-coded minimum amount required for staking in the protocol. 
  2. Stake Proxy Contract:
     1. The output stake box must contain the staked DAO tokens from the input stake proxy box.
     2. The output stake box adopts the same stakeTime parameter stored in R4.

#### Condition 5: Valid User Wallet Box
  1. Stake State Contract:
     1. The box contract must be guarded by the user's PK stored in R5 of the stake proxy box.
     2. The box must contain the stake key NFT, received from the stake state box.
  2. Stake Proxy Contract:
     1. Same as in the stake state contract.

#### Condition 6: Valid New Staking Incentive Box
  1. Stake Proxy Contract:
     1. The box value must contain the hard-coded amount of ERG.
     2. The blake2b256 hash of the output contract must be the same as the hard-coded constant within the contract of the stake proxy box.

#### Condition 7: Valid Tx Executor Box
  1. Stake Proxy Contract:
     1. The box must contain the hard-coded amount of ERG.

#### Condition 8: Valid Miner Fee Box
  1. Stake Proxy Contract:
     1. The box must contain the hard-coded amount of ERG.

#### Condition 9: Valid Output Size
  1. Stake Proxy Contract:
     1. The total output size must be 6.

---

## Action: Emit

The emit transaction starts the next staking cycle. The checkpoint of the stake state box increases. Emission tokens are taken from the stake pool and added to the new emission box that will distribute those rewards. The emission box takes a snapshot of the amount of stake boxes. A new staking cycle cannot start until the amount of stakers value stored in the emission box drops to 0. Thus, all stake boxes must go through the compound transaction before the new staking cycle.

### Data-Inputs

  - None

### Inputs

  0. Stake State Box
  1. Stake Pool Box
  2. Emission Box
  3. Staking Incentive Box

### Outputs

  0. New Stake State Box
  1. New Stake Pool Box
  2. New Emission Box
  3. Emission Fee Box
  4. New Staking Incentive Box
  5. Tx Operator Output Box

### Action Conditions

#### Condition 1: Valid Emit Inputs
  1. Stake State Contract:
     1. The input stake pool box must have the stake pool NFT as a token.
     2. The input size must be greater than or equal to 3.
  2. Stake Pool Contract:
     1. The stake state box must contain the stake state NFT as a token.
     2. The second input box id must be the current stake pool box guarded by the stake pool contract with the correct box id.
  3. Emission Contract:
     1. The stake state box contains the stake state NFT.
     2. The third input box is the current emission box with guarded by the emission contract with the correct box id.
  4. Staking Incentive Contract:
    1. The stake state box must contain the stake state NFT.
    2. The emission box must contain the emission NFT.
    3. The last input box must be the current staking incentive box guarded by the correct staking incentive contrat with the correct box id.

#### Condition 2: Valid Emission Input Box
  1. Stake State Contract:
     1. The emission box contains the emission NFT.
     2. The input emission box

#### Condition 3: Valid New Stake State Box
  1. Stake State Contract:
     1. Valid Self Replication
        1. Same as in the [Stake](<#action-stake>) action.
     2. The emission cycle checkpoint parameter is increased by 1.
     3. The amount of stakers remains constant.
     4. The checkpoint timestamp increments by the emission cycle duration amount.
     5. The checkpoint timestamp must be less than the timestamp of the block pre-header.
     6. The amount of stake tokens in the stake state box remains constant.
  2. Stake Pool Contract:
     1. The total amount of tokens staked is updated and increases according to: 
        - **total amount staked = current amount staked + (emission amount - emission fee amount) - emission dust**

#### Condition 4: Valid New Stake Pool Box
  1. Stake Pool Contract:
     1. The ERG value remains constant.
     2. The box is guarded by the same contract.
     3. The stake pool NFT identifier remains the same.
     4. Valid Remaining Stake Pool Tokens Amount
        1. If the alloted emission amount of tokens can be removed from the stakepool
           1. Check that the new stake pool box maintains the same DAO token id.
           2. Check that the amount of DAO tokens removed from the stake pool is only the alloted emission amount.
        2. If no emission tokens can be removed from the stake pool
           1. Check that there are no more DAO tokens in the stake pool and the only token remaining is the stake pool NFT identifier.
     5. The new stake pool box has the same alloted emission amount parameter stored in R4.
     6. The DAO token id stored in R5 must remain the same.

#### Condition 5: Valid New Emission Box
  1. Emission Contract:
     1. The ERG value remains constant.
     2. The box is guarded by the same contract.
     3. The Total Amount Staked, Checkpoint, and Stakers parameters stored in R4 of the new emission box are unchanged from those in R4 of the input stake state box.
     4. If emission tokens can be withdrawn from the stake pool, update the emission amount of the new emission box in R4, it will contain 99% of the alloted emission amount designated wihtin R4 of the stake pool box. The remaining 1% goes to the ErgoPad treasury.
     5. The new emission box contains the same NFT token id as the input emission box.
     6. The new emission box contains the same issued DAO token id as the current emission box.
     7. The new emission box contains the same amount of emission DAO tokens designated within R4 of the new emission box, which corresponds to the alloted emission amount designated within R4 of the stake pool box.

#### Condition 5: Valid New Staking Incentive Box
  1. Staking Incentive Contract
     1. The new staking incentive box must be able to provide the necessary ERG rewards to the tx execution bot and the miner.
     2. The new box must be guarded with the same contract as the input staking incentive box.
#### Condition 6: Valid Emission Fee Box
  1. Stake Pool Contract:
     1. The contract of the output box is the same as the hard-coded address within the contract of the stake pool box.
     2. The emission fee box contains the minimum ERG value for box existance.

#### Condition 7: Valid New Tx Operator Output Box
  1. Staking Incentive Contract:
     1. The tx operator receives the default hard-coded ERG reward amount for executing the emit tx.

#### Condition 8: Valid Miner Fee Box
  1. Staking Incentive Contract
     1.  The miner receives the default hard-coded miner fee reward.

---

## Action: Compound

Distribute the DAO token funds from the new emission box to the stake boxes. Each stake box will go through the compound tx exactly once each emission cycle. The emission box distributed rewards based on the total amount staked (the recorded parameter) and the stake amount within each stake box. The checkpoint in the stake box is increased to make sure it is not part of the same staking cycle more than once.

### Data-Inputs
- None

### Inputs
0. Emisison Box
1. Stake Boxes
2. Staking Incentive Box

### Outputs
0. New Emission Box
1. New Stake Boxes
2. New Staking Incentive Box
3. Tx Operator Output Box

### Action Conditions

#### Condition 1: Valid Input Size
1. Staking Incentive Contract:
#### Condition 1: Valid Compound Inputs
1. Emission Contract:
2. Stake Contract:
3. Staking Incentive Contract:
#### Condition 2: Valid New Emission Box
1. Emission Contract:
#### Condition 3: Valid New Stake Boxes
1. Stake Contract:
   1. Valid Self Replication
#### Condition 4: Valid New Staking Incentive Box
1. Staking Incentive Contract:
#### Condition 5: Valid Tx Operator Output Box
1. Staking Incentive Contract:
#### Condition 6: Valid Miner Fee Box
1. Staking Incentive Contract:

---

## Action: Unstake

The user wishes to remove their staked tokens from the staking protocol, using their stake key. Their are two options, a full unstake where the user withdraws all funds from the system and loses their stake key, or a partial unstake where only a portion of the funds staked will be removed and the user retains their stake key.

### Data-Inputs
- None

### Inputs
0. Stake State Box
1. Stake box
2. Unstake Proxy Box
3. Staking Incentive Box

### Outputs
#### Full Unstake:
0. New Stake State Box
1. User Wallet Box
2. New Staking Incentive Box
3. Tx Operator Output Box
#### Partial Unstake:
0. New Stake State Box
1. User Wallet Box
2. New Stake Box
3. New Staking Incentive Box
4. Tx Operator Output Box
### Action Conditions

### Full Unstake
#### Condition 1: Valid Unstake Inputs
1. Stake State Contract:
2. Stake Contract:
3. Unstake Proxy Contract:
#### Condition 2: Valid Full Unstake
1. Stake State Contract:
   1. Valid Unstake Input And Outputs

### Partial Unstake

#### Condition 1:

#### Condition 2:

---

## Action: Add Stake

This actions does this.

### Data-Inputs
- None
### Inputs
0.

### Outputs
0.
### Action Conditions

#### Condition 1:
...

#### Condition 2:
...
   
---

## Action: Consolidate

This actions does this.

### Data-Inputs
- None

### Inputs
0. 

### Outputs
0. 

### Action Conditions

#### Condition 1:
...

#### Condition 2:
...
   
---

## Action: Remove Funds

This actions does this.

### Data-Inputs
- None
### Inputs
0. 
### Outputs
0. 
### Action Conditions

#### Condition 1:
...

#### Condition 2:
...
   
---

## Action: Refund

This actions does this.

### Data-Inputs
- None
### Inputs
0. 
### Outputs
0. 
### Action Conditions

#### Condition 1:
...

#### Condition 2:
...
   
---

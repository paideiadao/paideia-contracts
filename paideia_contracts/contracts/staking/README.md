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

# Actions

1. [Bootstrap Stake Pool](#action-bootstrap-stake-pool)
2. [Stake](#action-stake)
3. [Emit](#action-emit)
4. [Compound](#action-compound)
5. [Unstake](#action-unstake)
6. [Add Stake](#action-add-stake)

---

## Stage: Staking Incentive

Proxy contract that

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Stake Proxy

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Stake State

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Stake Pool

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Staking

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Emission

In this stage, the user has staked their DAO tokens. The next emission snapshot begins, where emission tokens are taken from the stake pool and ready to be distributed to stake holders.

### Registers

- R4: Coll[Long]
  - 0: Total amount staked
  - 1: Checkpoint
  - 2: Stakers
  - 3: Emission amount

- Tokens:
  - 0:
    - Emission NFT: Indentifier for the emission box.
    - Amount: 1
  - 1:
    - DAO Token ID: Tokens to be emitted by the DAO.
    - Amount: <= DAO token emission amount.

### Hard-Coded Constants

- Stake State NFT: NFT identifying the stake state box.
- Stake Token ID: Token proving that the stake box was created properly.
- Staked Token ID: Token identifier for the token distributed by the DAO.

### Context Extension Variables

None

### Mandatory Stage Spending Conditions

None

### Action Paths

- [Emit](#action-emit)
- [Compound](#action-compound)
  
---

## Stage: Unstake Proxy

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Stage: Add Stake Proxy

This stage does this.

### Registers

- R4: ...
- R4: ...

### Hard-Coded Constants

- ...

### Context Extension Variables

1. ...

### Mandatory Stage Spending Conditions



### Action Paths

- [x Action](<#X-Action>)
  
---

## Action: Bootstrap Stake Pool

This action does this.

### Inputs

1. Input box does this.

### Outputs

1. A box that does this.

---

## Action: Stake

This actions does this.

### Data-Inputs

#### Data-Input 1

...

#### Data-Input 2

...


### Inputs

#### Input 1
...

#### Input 2
...

### Outputs

#### Output 1
...

#### Output 2
...

### Action Conditions

#### Condition 1
...

#### Condition 2
...
   
---

## Action: Emit

The emit transaction starts the next staking cycle. The checkpoint of the stake state box increases. Emission tokens are taken from the stake pool and added to the new emission box that will distribute those rewards. The emission box takes a snapshot of the amount of stake boxes. A new staking cycle cannot start until the amount of stakers value stored in the emission box drops to 0. Thus, all stake boxes must go through the compound transaction before the new staking cycle.

### Data-Inputs

None

### Inputs

#### Input 1
...

#### Input 2
...

### Outputs

#### Output 1
...

#### Output 2
...

### Action Conditions

#### Condition 1
...

#### Condition 2
...
   
---

## Action: Compound

This actions does this.

### Data-Inputs

#### Data-Input 1

...

#### Data-Input 2

...


### Inputs

#### Input 1
...

#### Input 2
...

### Outputs

#### Output 1
...

#### Output 2
...

### Action Conditions

#### Condition 1
...

#### Condition 2
...
   
---

## Action: Unstake

This actions does this.

### Data-Inputs

#### Data-Input 1

...

#### Data-Input 2

...


### Inputs

#### Input 1
...

#### Input 2
...

### Outputs

#### Output 1
...

#### Output 2
...

### Action Conditions

#### Condition 1
...

#### Condition 2
...
   
---

## Action: Add Stake

This actions does this.

### Data-Inputs

#### Data-Input 1

...

#### Data-Input 2

...


### Inputs

#### Input 1
...

#### Input 2
...

### Outputs

#### Output 1
...

#### Output 2
...

### Action Conditions

#### Condition 1
...

#### Condition 2
...
   
---
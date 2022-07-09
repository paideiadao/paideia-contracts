# Paideia Governance Protocol

EIP-6 specification for the Paideia governance protocol.

# Stages

1. [Paideia Origin](#stage-paideia-origin)
2. [DAO Config](#stage-dao-config)
3. [Paideia Mint](#stage-paideia-mint)
4. [Proto DAO Proxy](#stage-proto-dao-proxy)
5. [Proto DAO](#stage-proto-dao)
6. [DAO](#stage-dao)
7. [DAO Vote Proxy](#stage-dao-vote-proxy)
8. [DAO Vote](#stage-dao-vote)
9. [DAO Cast Vote Proxy](#stage-dao-cast-vote-proxy)
10. [DAO Proposal Proxy](#stage-dao-proposal-proxy)
11. [DAO Proposal](#stage-dao-proposal)
12. [DAO Action](#stage-dao-action)
13. [DAO Treasury](#stage-dao-treasury)

# Actions

1. [Create Proto DAO](#action-create-proto-dao)
2. [Mint Token](#action-mint-token)
3. [Create DAO](#action-create-dao)
4. [Create DAO Vote Box](#action-create-dao-vote-box)
5. [Create DAO Proposal](#action-dao-proposal)
6. [Cast Vote](#action-cast-vote)

# Tokens/NFTs

| Name | Type | Description |
| --- | --- | --- |
| Paideia Origin | NFT | Identifier for Paideia Origin box |
| Paideia DAO | Token | Verified Paideia DAO |
| DAO Config | Token | Verified DAO Config token (Unique for each DAO) |

---

## Stage: Paideia Origin

The contract holding the Paideia DAO tokens ensuring only DAO's created in the correct way will hold a Paideia DAO token.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Index of config box to use for fees |
| R5 | Coll[Coll[Byte]] | 0 | Token Id of config box | 

### Assets

| Token Name | Token Amount |
| --- | --- |
| Paideia Origin | 1 |
| Paideia DAO | Inf |

### Mandatory Stage Spending Conditions



### Action Paths

- [Create Proto DAO](#action-create-proto-dao)
  
---

## Stage: DAO Config

A DAO Config box acts as a data input for other contracts in the governance setup or DAO specific contracts. They can be updated through proposals. The first Long and Coll[Byte] registers are reserved for identifying the config box and the proposal token id. A special instance with index 0 will contain the main DAO settings that are to be set for each DAO and will be created in the DAO creation process. New config boxes can be created through proposals.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Config box index |
| R5 | Coll[Coll[Byte]] | 0 | DAO Proposal token | 

### Assets

| Token Name | Token Amount |
| --- | --- |
| DAO Config | 1 |

### Mandatory Stage Spending Conditions



### Action Paths

- [Update Config](#action-update-config)
  
---

## Stage: Paideia Mint

During DAO creation many tokens will be minted. This contract will hold minted tokens until they can be locked into the appropiate contracts. By using this contract in conjunction with the Proto DAO contract we ensure that the correct amounts are minted and all the tokens are locked in the contracts, preventing malicious users from keeping some tokens for themselves (and later on create malicious proposals/actions).

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Minted token | X |

### Mandatory Stage Spending Conditions


### Action Paths

- [Create DAO](#action-create-dao)
  
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
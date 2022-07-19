# Paideia Governance Protocol

EIP-6 specification for the Paideia governance protocol. In this protocol we work with the concept of proposals and actions. These are generic terms, specific proposals and actions will be implemented over time and documented separately to keep this document maintainable. A DAO can use custom proposals and actions, but this is for advanced use only, as it can potentially pose a risk to the DAO.

## References

This document describes the main Paideia governance protocol. It is kept generic to allow for extension in the future. Follow the links below to read up on specific descriptions:

- [Paideia Data Types](DataTypes.md)
- [Special Config Boxes](SpecialConfigs.md)
- [Proposal types](proposals/README.md)
- [Action types](actions/README.md)

# Contracts

1. [Paideia Origin](#contract-paideia-origin)
2. [DAO Config](#contract-dao-config)
3. [Paideia Mint](#contract-paideia-mint)
4. [Proto DAO Proxy](#contract-proto-dao-proxy)
5. [Proto DAO](#contract-proto-dao)
6. [DAO](#contract-dao)
7. [Vote Proxy](#contract-vote-proxy)
8. [Vote](#contract-vote)
9. [Cast Vote Proxy](#contract-cast-vote-proxy)
10. [Proposal Proxy](#stcontractage-proposal-proxy)
11. [Proposal](#contract-proposal)
12. [Action Proxy](#contract-action-proxy)
13. [Action](#contract-action)
14. [Treasury](#contract-treasury)

# Transactions

1. [Create Proto DAO Proxy](#transaction-create-proto-dao-proxy)
1. [Create Proto DAO](#transaction-create-proto-dao)
2. [Mint Token](#transaction-mint-token)
3. [Create DAO](#transaction-create-dao)
4. [Create Vote Proxy](#transaction-create-vote-proxy)
4. [Create Vote](#transaction-create-vote)
4. [Create Proposal Proxy](#transaction-create-proposal-proxy)
5. [Create Proposal](#transaction-proposal)
6. [Cast Vote Proxy](#transaction-cast-vote-proxy)
6. [Cast Vote](#transaction-cast-vote)
7. [Evaluate Proposal](#transaction-evaluate-proposal)
7. [Perform Action](#transaction-perform-action)

# Tokens/NFTs

| Name | Type | Description |
| --- | --- | --- |
| Paideia Origin | NFT | Identifier for Paideia Origin box |
| Paideia DAO | Token | Verified Paideia DAO |
| Config* | Token | Verified Config token |
| DAO NFT* | NFT | Unique identifier for DAO box |
| Proposal* | Token | Verified Proposal token |
| Vote* | Token | Verified Vote token |
| Action* | Token | Verified Action token |

*: Unique for each DAO

---

## Contract: Paideia Origin

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

### Transaction

- [Create Proto DAO](#transaction-create-proto-dao)
  
---

## Contract: DAO Config

A DAO Config box acts as a data input for other contracts in the governance setup or DAO specific contracts. They can be updated through proposals. The first Long register is reserved for identifying the config box. A special instance with index 0 will contain the main DAO settings that are to be set for each DAO and will be created in the DAO creation process. New config boxes can be created through proposals.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Config box index |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Config | 1 |

### Transactions

- [Perform Action](#transaction-perform-action)
  
---

## Contract: Paideia Mint

During DAO creation many tokens will be minted. This contract will hold minted tokens until they can be locked into the appropiate contracts. By using this contract in conjunction with the Proto DAO contract we ensure that the correct amounts are minted and all the tokens are locked in the contracts, preventing malicious users from keeping some tokens for themselves (and later on create malicious proposals/actions).

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Minted token | X |


### Transactions

- [Create DAO](#transaction-create-dao)
  
---

## Contract: Proto DAO Proxy

This is the contract the user sends funds to and defines in the registers the relevant parameters for DAO creation. If the parameters are valid and the fee sufficient the DAO creation process will be initiated by creating a Proto DAO box.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Coll[Byte]] | 0 | Dao Name |
| | | 1 | Governance token id |
| R5 | Coll[Long] | 0 | Min quorum |
| | | 1 | Min proposal time |
| | | 2 | Stake pool allocation |
| | | 3 | Emission amount |
| | | 4 | Emission time |
| | | 5 | Emission Start |
| R6 | Coll[Coll[Byte]] | 0-N | Hash of whitelisted proposal type |
| R7 | Coll[Coll[Byte]] | 0-M | Hash of whitelisted action type |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Paideia | Fee amount |


### Transactions

- [Create Proto DAO Proxy](#transaction-create-proto-dao-proxy)
- [Create Proto DAO](#transaction-create-proto-dao)
  
---

## Contract: Proto DAO

This contract ensures the DAO is created correctly including the minting of the tokens/nft's.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Coll[Byte]] | 0 | Dao Name |
| | | 1 | Governance token id |
| | | 2 | DAO NFT |
| | | 3 | Config |
| | | 4 | Vote |
| | | 5 | Proposal |
| | | 6 | Action |
| | | 7 | Stake state |
| | | 8 | Stake pool |
| | | 9 | Emission |
| | | 10 | Stake |
| R5 | Coll[Long] | 0 | Min quorum |
| | | 1 | Min proposal time |
| | | 2 | Stake pool allocation |
| | | 3 | Emission amount |
| | | 4 | Emission time |
| | | 5 | Emission Start |
| R6 | Coll[Coll[Byte]] | 0-N | Hash of whitelisted proposal type |
| R7 | Coll[Coll[Byte]] | 0-M | Hash of whitelisted action type |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Paideia DAO | 1 |

### Transactions

- [Create DAO](#transaction-create-dao)
- [Mint Token](#transaction-mint-token)
  
---
  
## Contract: DAO

This contract lies at the center of a DAO. Each DAO will have one DAO box to ensure verification of proposals and vote boxes etc. It keeps track of indexes for config, proposal and action boxes.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Config index |
| | | 1 | Proposal index |
| | | 2 | Action index |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Paideia DAO | 1 |
| DAO NFT | 1 |
| Config | Inf |
| Proposal | Inf |
| Vote | Inf |
| Action | Inf |

### Transactions
- [Create Proposal](#transaction-create-proposal)
- [Create Vote](#transaction-create-vote)
- [Perform Action](#transaction-perform-action)

---

## Contract: Vote Proxy

A DAO member that wants to participate in either creating a proposal or voting on a proposal needs to have a vote box. A vote box depends on a stake box and as such requires the stake key from the member.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Coll[Byte]] | 0 | User ergotree |
| | | 1 | DAO NFT |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Stake key | 1 |

### Transactions
- [Create Vote](#transaction-create-vote)
  
---

## Contract: Vote

A vote box is used to record the votes cast by the user and locks the stake key to prevent double voting.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Coll[Byte]] | 0 | Vote key |
| R5 | Coll[(Int,(Byte,Long))] | x | A vote registration with the following structure: (Proposal Index,(Vote option index, Vote amount)) |
| R6 | Coll[Long] | 0 | Unlock time |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Vote | 1 |
| Stake key | 1 |

### Transactions
- [Cast Vote](#transaction-cast-vote)
  
---

## Contract: Cast Vote Proxy

To cast a vote a user sends his vote key to a cast vote proxy along with the desired vote.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Coll[Byte]] | 0 | User ergotree |
| R5 | Coll[(Int,(Byte,Long))] | 0 | A vote registration with the following structure: (Proposal Index,(Vote option index, Vote amount)) |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Vote key | 1 |

### Transactions
- [Cast Vote](#transaction-cast-vote)

---

## Contract: Proposal Proxy

A proposal can be created by a user by creating a Proposal Proxy box, including the required assets and parameters in the registers. Each proposal type will have it's own proxy to ensure validation. DAO's can vote on including more/new proposal types.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4-R9 | Any | - | Depends on proposal type |

### Assets

| Token Name | Token Amount |
| --- | --- |

### Transactions
- [Create Proposal Proxy](#transaction-create-proposal-proxy)
- [Create Proposal](#transaction-create-proposal)

---

## Contract: Proposal

A proposal can be created by a user by creating a Proposal Proxy box, including the required assets and parameters in the registers. Each proposal type will have it's own proxy to ensure validation. DAO's can vote on including more/new proposal types.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Proposal index - A unique index for this proposal assigned by the DAO |
| | | 1 | Minimum quorum needed to pass the proposal (in %) |
| | | 2 | End timestamp (in ms) at which points voting is no longer possible and the proposal can be evaluated |
| | | 3 | Evaluated (0 or 1) |
| R5 | Coll[Coll[Byte]] | 0 | Proposal title |
| | | 1 | Proposal description |
| | | 2-N+2 | Option description | 
| R6 | Coll[(Long,Boolean)] | 0-N | (Vote tally, passed) |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Proposal | 1 |

### Transactions
- [Cast Vote](#transaction-cast-vote)
- [Perform Action](#transaction-perform-action)

---

## Contract: Action Proxy

An action can be created by a user by creating an Action Proxy box, including the required assets and parameters in the registers. Each action type will have it's own proxy to ensure validation. DAO's can vote on including more/new action types.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4-R9 | Any | - | Depends on action type |

### Assets

| Token Name | Token Amount |
| --- | --- |

### Transactions
- [Create Proposal Proxy](#transaction-create-proposal-proxy)
- [Create Proposal](#transaction-create-proposal)
  
---

## Contract: Action

An action defines some kind of activity which is linked to a passed proposal.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Action index |
| | | 1 | Proposal index |
| R5-R9 | Any | - | Depends on action type |

### Assets

| Token Name | Token Amount |
| --- | --- |
| Action | 1 |


### Transactions
- [Perform Action](#transaction-perform-action)

---

## Contract: Treasury

The treasury holds the assets belonging to the DAO, these can only be spent through actions/passed proposals.

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |

### Assets

| Token Name | Token Amount |
| --- | --- |

### Transactions
- [Perform Action](#transaction-perform-action)

---

## Transaction: Create Proto DAO Proxy

This is a user intiated transaction to initiate the "create DAO" process. 

### Inputs

1. User inputs with the needed fee.

### Outputs

1. [Create DAO Proxy](#contract-proto-dao-proxy)

---

## Transaction: Create Proto DAO

Creation of the proto DAO box.

#### Data-Inputs

1. [Paideia Fee Config](#contract-dao-config)

### Inputs

1. [Paideia Origin](#contract-paideia-origin)
2. [Proto DAO Proxy](#contract-proto-dao-proxy)

### Outputs

1. [Paideia Origin](#contract-paideia-origin)
2. [Proto DAO](#contract-proto-dao)
3. [Paideia Treasury](#contract-treasury)

### Transaction Conditions

1. Data input is correct
2. Fee is correct
3. Proto dao contract is correct with registers filled correctly

---

## Transaction: Mint Token

Mints a token during the DAO creation process.

### Inputs

1. [Proto DAO](#contract-proto-dao)

### Outputs

1. [Proto DAO](#contract-proto-dao)
2. [Paideia Mint](#contract-paideia-mint)

### Transaction Conditions

1. Minted token has correct amount
2. Minted token stored in proto dao register
   
---

## Transaction: Create DAO

Once all tokens are minted, the DAO can be created.

### Inputs

1. [Proto DAO](#contract-proto-dao)
2. [Paideia Mint](#contract-paideia-mint)

### Outputs

1. [DAO](#contract-dao)
2. [DAO Config](#contract-dao-config)
3. Stake State
4. Stake Pool
5. Emission

### Transaction Conditions

1. Token id's match the corresponding tokens in the different boxes and registers
   
---

## Transaction: Create Vote Proxy

A user initiated transaction to create a vote box for the user.

### Inputs

1. Userinput with stake key

### Outputs

1. [Vote Proxy](#contract-vote-proxy)
   
---

## Transaction: Create Vote

The vote box is created and the user gets his vote key.

### Data-Inputs

1. Stake
2. [DAO Config](#contract-dao-config)

### Inputs

1. [DAO](#contract-dao)
2. [Vote Proxy](#contract-vote-proxy)

### Outputs

1. [DAO](#contract-dao)
2. [Vote](#contract-vote)
3. User box with vote key

### Transaction Conditions

1. DAO Config is correct
2. Stake data input is verified stake box according to dao config
3. Stake key corresponds to stake box
   
---

## Transaction: Create Proposal Proxy

A user initiated transaction to create a proposal and it's associated actions. The output should be 1 proposal proxy and 0 or more action proxy's.

### Inputs

1. Userinput with vote key and fee

### Outputs

1. [Proposal Proxy](#contract-proposal-proxy)
2. [Action Proxy](#contract-action-proxy)
   
---

## Transaction: Create Proposal

A proposal is created along with the actions related to it.

### Data-Inputs

1. [DAO Config](#contract-dao-config)

### Inputs

1. [DAO](#contract-dao)
2. [Proposal Proxy](#contract-proposal-proxy)
3. [Action Proxy](#contract-action-proxy)

### Outputs

1. [DAO](#contract-dao)
2. [Proposal](#contract-proposal)
3. [Action](#contract-action)
4. User output with vote key
   
---

## Transaction: Cast Vote Proxy

A user initiated transaction to initiate a vote on a proposal

### Inputs

1. Userinput with vote key

### Outputs

1. [Cast Vote Proxy](#contract-cast-vote-proxy)
   
---

## Transaction: Cast Vote

A vote is cast on a proposal

### Data-Inputs

1. Stake

### Inputs

1. [Proposal](#contract-proposal)
2. [Vote](#contract-vote)
2. [Cast Vote Proxy](#contract-cast-vote-proxy)

### Outputs

1. [Proposal](#contract-proposal)
2. [Vote](#contract-vote)
2. User output with vote key

### Transaction Conditions

1. Vote power does not exceed stake amount
2. Proposal correctly updated
3. Vote correctly updated
   
---

## Transaction: Evaluate Proposal

Evaluate a proposal to finalize it's state, allowing actions to be taken accordingly.

### Data-Inputs

1. Stake State

### Inputs

1. [Proposal](#contract-proposal)

### Outputs

1. [Proposal](#contract-proposal)

### Transaction Conditions

1. Enough time has passed
2. Enough votes cast to pass quorum % (100% quorum is total amount staked)
   
---

## Transaction: Perform Action

Evaluate a proposal to finalize it's state, allowing actions to be taken accordingly.

### Data-Inputs

1. [Proposal](#contract-proposal)

### Inputs

1. [Action](#contract-action)
2. Depends on action type

### Outputs

1. Depends on action type

### Transaction Conditions

1. Proposal passed and matches the action
   
---
# Proposal type: Simple

The simple proposal type only has two options, yes or no. A minimum quorum % can be set and an end time within which the voting needs to happen. If after the set time the "yes" option has a majority vote and the minimum quorum has been reached the proposal is evaluated as passed and any associated actions can be executed.

---

## Contract: Proposal Simple Proxy

The proxy confirms the resulting Simple Proposal contains the correct values in the registers and that any actions only relate to the Yes option.

### Assets

| Token Name | Amount |
| --- | --- |
| Vote key | 1 |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Minimum quorum needed to pass the proposal (in %) |
| | | 1 | End timestamp (in ms) at which points voting is no longer possible and the proposal can be evaluated |
| R5 | Coll[Coll[Byte]] | 0 | Proposal title |
| | | 1 | Proposal description |
| | | 2 | User ergotree |

### Transactions
- [Create Simple Proposal Proxy](#transaction-create-simple-proposal-proxy)
- [Create Simple Proposal](#transaction-create-simple-proposal)

---

## Contract: Proposal Simple

The simple proposal contract

### Assets

| Token Name | Amount |
| --- | --- |
| Proposal | 1 |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Proposal index - A unique index for this proposal assigned by the DAO |
| | | 1 | Minimum quorum needed to pass the proposal (in %) |
| | | 2 | End timestamp (in ms) at which points voting is no longer possible and the proposal can be evaluated |
| | | 3 | Evaluated (0 or 1) |
| R5 | Coll[Coll[Byte]] | 0 | Proposal title |
| | | 1 | Proposal description |
| | | 2 | Yes |
| | | 3 | No | 
| R6 | Coll[(Long,Boolean)] | 0-1 | (Vote tally, passed) |

### Transactions
- [Create Simple Proposal](#transaction-create-simple-proposal)
- [Evaluate Simple Proposal](#transaction-evaluate-simple-proposal)

---

## Transaction: Create Simple Proposal Proxy

A user initiated transaction to create a simple proposal and it's associated actions. The output should be 1 simple proposal proxy and 0 or more action proxy's.

### Inputs

1. Userinput with vote key and fee

### Outputs

1. [Simple Proposal Proxy](#contract-simple-proposal-proxy)
2. [Action Proxy](../../actions/README.md)
   
---

## Transaction: Create Simple Proposal

A proposal is created along with the actions related to it.

### Data-Inputs

1. [DAO Config](#contract-dao-config)

### Inputs

1. [DAO](#contract-dao)
2. [Proposal Proxy](#contract-simple-proposal-proxy)
3. [Action Proxy](../../actions/README.md)

### Outputs

1. [DAO](#contract-dao)
2. [Simple Proposal](#contract-simple-proposal)
3. [Action](../../actions/README.md)
4. User output with vote key
   
---
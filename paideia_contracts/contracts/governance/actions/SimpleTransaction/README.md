# Action Type: Simple Transaction

This action supports sending funds from the treasury to one box with up to R7 filled out.

## Contract: Action Simple Transaction Proxy

The user defines here what the simple transaction action needs to look like.

### Assets

| Token Name | Amount |
| --- | --- |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Option index - the option of the proposal which needs to pass for this action to execute |
| | | 1-4 | Data type for registers ([See data type list](../../DataTypes.md)) |
| | | 5 | Amount of nanoerg to send |
| | | 6-N | Token amounts |
| R5 | Coll[Coll[Byte]] | 0 | Proposition bytes of desired output box |
| | | 1-N | Token id's |
| R6-R9 | Any | - | Registers of desired output box |

### Transactions

- [Create Proposal Proxy](../../README.md#transaction-create-proposal-proxy)
- [Create Proposal](../../README.md#transaction-create-proposal)

---

## Contract: Action Simple Transaction

This contract ensures the funds are send to the correct output and any change is returned to the treasury.

### Assets

Of course the first token needs to be a valid Action token

| Token Name | Amount |
| --- | --- |
| Action | 1 |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Proposal index - the proposal this action relates to |
| | | 1 | Option index - the option of the proposal which needs to pass for this action to execute |
| | | 2-5 | Data type for registers ([See data type list](../../DataTypes.md)) |
| | | 6 | Amount of nanoerg to send |
| | | 7-N | Token amounts |
| R5 | Coll[Coll[Byte]] | 0 | Proposition bytes of desired output box |
| | | 1-N | Token id's |
| R6-R9 | Any | - | Registers of desired output box |

### Transactions

- [Create Proposal](../../README.md#transaction-create-proposal)
- [Simple Send](#transaction-simple-send)

---

## Transaction: Simple Send

The funds are send to the correct address with the correct registers.

### Data-Inputs

1. [Proposal](../../README.md#contract-proposal)
2. [DAO Config](../../SpecialConfigs.md#dao-config)

### Inputs

1. [Action Simple Transaction](#contract-action-simple-transaction)
2. [Treasury](../../README.md#contract-treasury)

### Outputs

1. Output
2. [Treasury (Change box)](../../README.md#contract-treasury)
   
---
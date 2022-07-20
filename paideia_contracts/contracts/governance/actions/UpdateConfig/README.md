# Action Type: Update Config

This action is used to update a config that is governed by the DAO.

## Contract: Action Update Config Proxy

The user defines here what the update config action needs to look like.

### Assets

| Token Name | Amount |
| --- | --- |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Option index - the option of the proposal which needs to pass for this action to execute |
| | | 1 | Config index |
| | | 2-7 | Data type for registers ([See data type list](../../DataTypes.md)) |
| R5-R9 | Any | - | - |

### Transactions

- [Create Proposal Proxy](../../README.md#transaction-create-proposal-proxy)
- [Create Proposal](../../README.md#transaction-create-proposal)

---

## Contract: Action Update Config

This contract ensures the updated config box is filled out with the correct values.

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
| | | 2 | Config index |
| | | 3-8 | Data type for registers ([See data type list](../../DataTypes.md)) |
| R5-R9 | Any | - | - |

### Transactions

- [Create Proposal](../../README.md#transaction-create-proposal)
- [Update Config](#transaction-update-config)

---

## Transaction: Update Config

The config box is updated with the registers filled out correctly.

### Data-Inputs

1. [Proposal](../../README.md#contract-proposal)
2. [DAO](../../README.md#contract-dao)

### Inputs

1. [Action Update Config](#contract-action-update-config)
2. [Config](../../README.md#contract-dao-config)

### Outputs

1. [Config](../../README.md#contract-dao-config)
   
---
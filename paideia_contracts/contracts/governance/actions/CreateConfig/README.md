# Action Type: Create Config

This action is used to create a new config that is to be governed by the DAO, including initial register values.

## Contract: Action Create Config Proxy

The user defines here what the create config action needs to look like.

### Assets

| Token Name | Amount |
| --- | --- |

### Registers

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Option index - the option of the proposal which needs to pass for this action to execute |
| | | 1-6 | Data type for registers ([See data type list](../../DataTypes.md)) |
| R5-R9 | Any | - | - |

## Contract: Action Create Config

This contract ensures the new config box is filled out with the correct values.

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
| | | 2-7 | Data type for registers ([See data type list](../../DataTypes.md)) |
| R5-R9 | Any | - | - |
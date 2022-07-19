# Paideia Actions

Below you can find a list of the different action types and which phase of development they currently are in. Underneath the list a description is given of the format an action needs to have to fit into the Paideia system. If you design and develop your own action type it is highly recommended to do this in a test DAO, before adding it to an existing DAO.

## Action type list

| Type name | Development Phase | Description |
| --- | --- | --- |
| [Create Config](CreateConfig/README.md) | Design | An action which is used to create a new config box for the DAO |
| [Update Config](UpdateConfig/README.md) | Design | An action which is used to update a config box for the DAO |
| [Simple Transaction](SimpleTransaction/README.md) | Design | Send a simple transaction with one output (+fee and change) from the treasury |

## Action design template

A Paideia Action consists of 2 contracts, an action proxy and the action itself.

The proxy's function is to ensure that the action has the right contract and that the registers are filled correctly.

The action needs to fit in the following template:

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

[Back to Paideia Goverance Protocol](../README.md)
# Paideia Proposals

Below you can find a list of the different proposal types and which phase of development they currently are. Underneath the list a description is given of the format a proposal needs to have to fit into the Paideia system. If you design and develop your own proposal type it is highly recommended to do this in a test DAO, before adding it to an existing DAO.

## Proposal type list

| Type name | Development Phase | Description |
| --- | --- | --- |
| [Simple](Simple/README.md) | Design | A simple proposal with 2 options to vote on, yes or no |

## Proposal design template

A Paideia proposal consists of 2 contracts, a proposal proxy and the proposal itself.

The proxy's function is to ensure that the proposal has the right contract and that the registers are filled correctly.

The proposal needs to fit in the following template:

### Assets

Of course the first token needs to be a valid Proposal token

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
| | | 2-N+2 | Option description | 
| R6 | Coll[(Long,Boolean)] | 0-N | (Vote tally, passed) |

[Back to Paideia Goverance Protocol](../README.md)
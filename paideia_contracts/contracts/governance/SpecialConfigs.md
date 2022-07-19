# Special Config Boxes

Each DAO will have special config boxes that always have the same format and hold important information related to the DAO. Not all special config boxes are in use yet, but are created empty to allow for future use. Config box 0-9 are special.

## DAO Config

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Special config box index 0 |
| | | 1 | R5 = Coll[Coll[Byte]] -> 4 |
| R5 | Coll[Coll[Byte]] | 0 | DAO Name |
| | | 1 | Stake State NFT |
| | | 2 | Stake Pool NFT |
| | | 3 | Emission NFT |

## DAO Whitelisted Proposal Types

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Special config box index 1 |
| | | 1 | R5 = Coll[Coll[Byte]] -> 4 |
| R5 | Coll[Coll[Byte]] | 0-N | Hash of whitelisted proposal ergotree |

## DAO Whitelisted Action Types

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Special config box index 2 |
| | | 1 | R5 = Coll[Coll[Byte]] -> 4 |
| R5 | Coll[Coll[Byte]] | 0-N | Hash of whitelisted action ergotree |

## Paideia Fee Config

This is a special config box belonging to the Paideia DAO. Since this is not a config box used by each DAO it is not one of the reserved config boxes, but instead the first regular config boxes belonging to the Paideia DAO, with config index 10.

| Register | Type | Index | Description |
| --- | --- | --- | --- |
| R4 | Coll[Long] | 0 | Config box index 10 |
| | | 1 | R5 = Coll[Long] -> 2 |
| R5 | Coll[Long] | 0 | DAO creation fee |
| | | 1 | Proposal creation fee |

[Back to Paideia Goverance Protocol](README.md)
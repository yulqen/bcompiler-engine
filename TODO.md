# TODO / v2.0 Development Notes

## Key features required for 2.0

Path to 2.0 involves replication of basic existing `bcompiler` functionality,
boiled down to:

1. Import data from populated templates

*2.0 implementation*: `bcompiler import templates --to-master/-m`. This
replaces `bcompiler compile/bcompiler` command in version 1.

2. Export data from master spreadsheet to blank templates

*2.0 implementation*: `bcompiler export master DATAMAP_PATH BLANK_PATH
MASTER_PATH`. This replaces `bcompiler -a` command in version 1.

3. API

The official API for bcompiler 1.0 is documented [here](https://bcompiler.readthedocs.io/en/latest/api.html).
Imports take the form `from bcompiler.api import project_data_from_master`. Currently 
only a few items are made available:

* Master
* Quarter
* FinancialYear
* Row

*2.0 implementation*: mirror existing API. Any changes should be marked as
deprecations and warnings issued to the user.

## Command line format

2.0 command line format is generally of the form: `**bcompiler** [verb] [object]
[arguments..] [options]`

## TODO

### Data validation

Currently working on 2 above. Current implementation removes data validation
(drop down lists) from target cells where it exists. Requirement is to maintain
the data validation. It is not required to be kept in all cases, but
`bcompiler` should strive to maintain the integrity of the spreadsheet file
wherever possible, and where not possible, issue warnings and flag in reports.

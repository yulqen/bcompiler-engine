# v1.1.0

* Basic type-checking (NUMBER, TEXT, DATE). Types are set using a "type" column
    in the datamap. Only datamap lines that receive a value of NUMBER, TEXT or
    DATE are currently validated - anything else is ignored and flagged.
* By default a CSV validation report is produced when running `datamaps import
  templates` revealing the result of type validation.
* Can set row limit when importing templates with `--rowlimit` flag in
    datamaps.
* Can run validation-only template imports. No master is produced - only
    a validation report (with `datamaps import templates -v`).

# v1.0.9

* Bug fixes.

# v1.0.8

* Now handles `datamaps config` commands. The `config.ini` can be revealed to
  the user and deleted.

# v1.0.7

* Added a row limit when importing data to prevent memory leak ([Issue #30](https://github.com/yulqen/bcompiler-engine/issues/30))

# v1.0.6

* added logging for process to write data from master to blank templates
  (`datamaps export master <MASTER_PATH>`) - [Issue
  #24](https://github.com/hammerheadlemon/bcompiler-engine/issues/24)

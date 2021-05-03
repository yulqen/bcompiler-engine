# v1.1.4

* Fix bug which resulted in one less file in zip being processed with `-z`
    flag.

# v1.1.3

* Enabled zip repository for import command. In datamaps, user can now use `-z`
    flag and point to zip file containing populated spreadsheets.

# v1.1.2

* Mainly internal refactoring and bugfixes.

# v1.1.0

See the [https://github.com/yulqen/datamaps/blob/master/CHANGELOG.md](datmaps
CHANGELOG).

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

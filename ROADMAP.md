# Roadmap / Development Notes

[datamaps](https://github.com/yulqen/datamaps) versions will mirror these
versions as long as there are significant-enough interface changes.


## Version 1.1.0

* Basic type-checking (NUMBER, TEXT, DATE)

## Version 1.2.0

NB: Formats used here are unstable.

* Rules-based type-checking
  * Cell cannot be blank (`NOBLANK`)
  * Dates must be within a certain range (`DATE>2020-01-10` or `DATE<2010-10-10`)
  * Numbers must be within a certain range (`NUMBER>10`)
  * Text length must be within a certain range (`TEXT<200`)
  * Text contains/choices (`TEXTCONTAIN Yes|No` or `TEXTNOTCONTAIN Yes|No`)

## Version 1.3.0

* Import direct to SQLite database
* Convert master files to SQLite database
* Removal of master as a storage medium

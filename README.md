## bcompiler-engine

![Tests](https://github.com/hammerheadlemon/bcompiler-engine/workflows/Tests/badge.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/yulqen/bcompiler-engine/badge.svg?branch=typechecking)](https://coveralls.io/github/yulqen/bcompiler-engine?branch=typechecking)

A new, faster, more efficient, more modular back end for
[Datamaps](http://datamaps.twentyfoursoftware.com), and for newer tools and improved interfaces.

A library that allows for controlled extraction and insertion of data to and
from spreadsheets used for collecting data. Part of a more modular overall
design, `bcompiler-engine` focuses on speed, simplicity and data validation. It
forms the primary back-end to
[datamaps](http://datamaps.twentyfoursoftware.com), and will
eventually have a suitable API making it easy for anyone designing an
application to use the datamaps philosophy - more on that coming soon.

### Highlights

* Brand new code, developed with the benefit of several years and multiple projects
    of hindsight.
* Extract data using multiple cores to do it faster.
* Type checking and rule-setting, allowing for greater confidence in integrity of data.
* Improved, modular design, powering *a brand new interface*, available soon.
* Designed to be packaged for more general distribution.

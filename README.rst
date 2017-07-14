
===============================
ret1: datajoint.io demo project
===============================
:Author: C.Turner
:Status: DRAFT

Overview
========

Example docker/datajoint.io demo project.

Builds a mysql + datajoint environment within docker, uses this to
process an example dataset.

Dataset is not publically available; logic expects data to be fetched
externally as a zip and placed into the current directory, where
it will be extracted into the heirarchy './crcns_ret-1'. This is
imported into the vm as '/data' and will be used by the execution
sequence.

Requirements
============

- docker, docker-compose (v2+)
- dataset as outlined in `Overview`_
- make

Usage
=====

To build/run the demo, first install `Requirements`_, then::

  $ make

this will extract the data archive, build the docker image, and
execute the demo.


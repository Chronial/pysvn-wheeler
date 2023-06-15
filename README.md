pysvn-wheeler
=============

Overview
--------

Wheel packages for [pysvn](http://pysvn.tigris.org/).

This is a setup script to build wheel packages for `pysvn`. The author of
`pysvn` provides only setup files for Windows which makes it difficult to use
`pysvn` in modern Python environments like a virtual environment. The
de-facto standard for Python packages is the `wheel` format which gives you
for instance the possibility to manage your packages with pip.

`pysvn-wheeler` extracts the `pysvn` setup file and creates a platform-specific
wheel package out of it. It doesn't compile `Subversion`, its dependencies and
`pysvn` from source. Because of that the content of a wheel and the
corresponding setup file is equal.

Usage
-----

`pysvn-wheeler` can be used to create a wheel from a `pysvn` installer.

* Download the pysvn installer you wish to convert.
* Make sure you use the same python version as the one want to create the wheel for.
* Install the wheel package: `python -m pip install wheel`
* `python wheeler.py <path_to_pysvn_installe>`

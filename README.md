This is the source tree or distribution for the rpy2 package.

<a href="https://drone.io/bitbucket.org/lgautier/rpy2/latest"><img alt="Build Status" src="https://drone.io/bitbucket.org/lgautier/rpy2/status.png">]</a>
<a href="https://crate.io/packages/rpy2/"><img alt="PyPi version" src="https://pypip.in/v/rpy2/badge.png"></a>

Installation
============

The distutils mechanism can be used:

    python setup.py install

The package is known to compile on Linux, WinXp and MacOSX
(provided that developper tools are installed).
In case you find yourself with this source without any idea
of what it takes to compile anything on your platform, do
consider looking for pre-compiled binaries.

Note that `python setup.py develop` will appear to work, but will result in an
installation from the `rpy` directory here. The namespaces will be
incorrect, so don't do that!

Documentation
=============

Documentation is available either in the source tree (to be built),
or online (see the rpy home page on sourceforge).

Testing
=======

The testing machinery uses the new unittest functionality, requiring python 2.7+
(or potentially the backported unittest2 library for older python, but this is
not supported). The test suite can be run (once rpy2 is installed) as follows:

    python -m rpy2.tests

By providing an argument, like "-v", you'll get verbose output.

Individual tests can be run as follows:

    python -m unittest rpy2.robjects.tests.testVector

Or test discovery can be used as follows:

    python -m unittest discover rpy2.robjects

Note that a problematic test is picked up if you do test discovery on the rpy2
root, and you'll get a segfault. So, always use `python -m rpy2.tests` to run
all tests.

License
=======

RPy2 can be used under the terms of either the GNU
General Public License Version 2 or later (see the file
gpl-2.0.txt).
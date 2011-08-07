

********
Overview
********


Background
==========

`Python`_ is a popular
all-purpose scripting language, while `R`_ (an open source implementation
of the S/Splus language)
is a scripting language mostly popular for data analysis, statistics, and
graphics. If you are reading this, there are good chances that you are
at least familiar with one of the two.

.. _Python: http://www.python.org
.. _R: http://www.r-project.org

Having an interface between both languages, and benefit from the respective
libraries of one language while working in the other language, appeared
desirable and an early option to achieve it was the RSPython project,
itself part of the `Omegahat project`_.

A bit later, the RPy project appeared and focused on providing simple and
robust access to R from within Python, with the initial Unix-only releases
quickly followed by Microsoft and MacOS compatible versions.
This project is referred to as RPy-1.x in the
rest of this document.

.. _Omegahat project: http://www.omegahat.org/RSPython

The present documentation describes RPy2, an evolution of RPy-1.x.
Naturally RPy2 is inspired by RPy, but also by A. Belopolskys's contributions
that were waiting to be included into RPy.

This effort can be seen as a redesign and rewrite of the RPy package, and this
unfortunately means there is not enough left in common to ensure compatibility.


Installation
============

Upgrading from an older release of rpy2
---------------------------------------

In order to upgrade one will have to first remove older
installed rpy2 packages then and only then install
the recent version of rpy2 wished.

To do so, or to check whether you have an earlier version
of rpy2 installed do the following in a Python console:

.. code-block:: python

   import rpy2
   rpy2.__path__

An error during the execution means that you do not have any older
version of rpy2 installed and you should proceed to the next section.

If this returns a string containing a path, you should go to that path
and removed all files and directories starting with *rpy2*. To make sure
that the cleaning is complete, open a new Python session and check that
trying to import rpy2 results in an error.


Requirements
------------

Python version 2.5 or greater, as well as R-2.8.0 or greater are required

Currently the development is done on UNIX-alike operating systems with the
following version for the softwares, and those are the recommended
versions to run rpy2 with.

======== ===========
Software Versions
======== ===========
 Python   2.6; 2.7
 R        2.13; 2.14
======== ===========

Python 2.4 might compile, but there is much less testing done with
those platforms and likely limited hope for free support.

Python 3.2 will install, but at the time of writing still has a couple
of minor issues.

.. warning::

   When building rpy2, it is checked that this is against a recommended
   version of R. Building against a different version is possible, although
   not supported at all, through the flag *--ignore-check-rversion*

   .. code-block:: bash

      python setup.py build_ext --ignore-check-rversion install
   
   Since recently, development R is no longer returning
   an R version and the check ends with an error
   "Error: R >= <some version> required (and R told 'development.').".
   The flag *--ignore-check-rversion* is then required in order to build.
   


.. note::

   When compiling R from source, do not forget to specify
   *--enable-R-shlib* at the *./configure* step.

   gcc-4.4 is used for compiling the C parts on Linux.
   gcc-4.0 seems to be the default on OS X Leopard and yet produce
   fully functional binaries.

.. note::

   If installing from a linux distribution, the Python-dev package will
   obviously be required to compile rpy2

.. note::

   On OS X, the *XCode* tools will be required in order to compile rpy2.


Download
--------

The following options are, or could be, available for download:

  * Source packages. Released versions are available on Sourceforge as well as
    on Pypy. Snapshots of the development version can downloaded from
    bitbucket

    .. note::
       The repository on bitbucket has several branches. Make sure to select
       the one you are interested in.

  * Pre-compiled binary packages for

    * Microsoft's Windows (releases are on Sourceforge, irregular snapshots
      for the dev version on bitbucket) - there is currently not support for rpy2-2.1

    * Apple's MacOS X (although Fink and Macports are available, there does not
      seem to be binaries currently available)

    * Linux distributions

`rpy2` has been reported compiling successfully on all 3 platforms, provided
that development items such as Python headers and a C compiler are installed.

.. note::
   Choose files from the `rpy2` package, not `rpy`.

.. note::
   The *easy_install* system can be used,
   although it is currently only provided for source
   (see :ref:`install-easyinstall`)

Linux precompiled binaries
--------------------------

Linux distribution have packaging systems, and rpy2 is present
in a number of them, either as a pre-compiled package or a source
package compiled on-the-fly.

.. note:: 

   Those versions will often be older than the latest rpy2 release.

Known distributions are: Debian and related (such as Ubuntu - often
the most recent thanks to Dirk Eddelbuettel), Suse, RedHat, Mandrake,
Gentoo.

On, OS X rpy2 is in Macports and Fink.


.. index::
  single: install;win32

Microsoft's Windows precompiled binaries
----------------------------------------

If available, the executable can be run; this will install the package
in the default Python installation.

For few releases in the 2.0.x series, Microsoft Windows binaries were contributed
by Laurent Oget from Predictix.

There is currently no binaries or support for Microsoft Windows (more for lack of
ressources than anything else).

.. index::
  single: install;source

Install from source
-------------------

.. _install-easyinstall:

easy_install and pip
^^^^^^^^^^^^^^^^^^^^

The source package is on the PYthon Package Index (PYPI), and the
*easy_install* or *pip* scripts can be used whenever available.
The shell command will then just be:

.. code-block:: bash

   easy_install rpy2

   # or

   pip install rpy2

Upgrading an existing installation is done with:

.. code-block:: bash

   easy_install rpy2 --upgrade

   # or

   pip install rpy2 --upgrade

Both utilities have a list of options and their respective documentation should
be checked for details.


.. _install-setup:

source archive
^^^^^^^^^^^^^^

To install from a downloaded source archive `<rpy_package>` do in a shell:

.. code-block:: bash

  tar -xzf <rpy_package>.tar.gz
  cd <rpy_package>
  python setup.py build install

This will build the package, guessing the R HOME from
the R executable found in the PATH.

Beside the regular options for :mod:`distutils`-way of building and installing
Python packages, it is otherwise possible to give explicitly the location for the R HOME:

.. code-block:: bash

   python setup.py build --r-home /opt/packages/R/lib install


Other options to build the package are:

.. code-block:: bash

   --r-home-lib # for exotic location of the R shared libraries

   --r-home-modules # for R shared modules


.. index::
  single: test;whole installation

Test an installation
--------------------

An installation can be tested for functionalities, and whenever necessary 
the different layers constituting the packages can be tested independently.

.. code-block:: bash

   python -m 'rpy2.tests'

On Python 2.6, this should return that all tests were successful.


Whenever more details are needed, one can consider running explicit tests.

.. code-block:: python

  import rpy2.tests
  import unittest

  # the verbosity level can be increased if needed
  tr = unittest.TextTestRunner(verbosity = 1)
  suite = rpy2.tests.suite()
  tr.run(suite)

.. note:: 

   Running the tests in an interactive session appear to trigger spurious exceptions
   when testing callback function raising exception. If unsure, just use the first way
   to test presented in the begining of this section.

.. warning::

  For reasons that remain to be elucidated, running the test suites used to leave the Python
  interpreter in a fragile state, soon crashing after the tests have been run.

  It is not clear whether this is still the case, but is recommended to terminate the 
  Python process after the tests and start working with a fresh new session.


To test the :mod:`rpy2.robjects` high-level interface:

.. code-block:: bash

  python -m 'rpy2.robjects.tests.__init__'

or for a full control of options

.. code-block:: python

  import rpy2.robjects.tests
  import unittest

  # the verbosity level can be increased if needed
  tr = unittest.TextTestRunner(verbosity = 1)
  suite = rpy2.robjects.tests.suite()
  tr.run(suite)

If interested in the lower-level interface, the tests can be run with:

.. code-block:: bash

  python -m 'rpy2.rinterface.tests.__init__'

or for a full control of options

.. code-block:: python

  import rpy2.rinterface.tests
  import unittest

  # the verbosity level can be increased if needed
  tr = unittest.TextTestRunner(verbosity = 1)
  suite = rpy2.rinterface.tests.suite()
  tr.run(suite)


Contents
========

The package is made of several sub-packages or modules:

:mod:`rpy2.rpy_classic`
-----------------------

Higher-level interface similar to the one in RPy-1.x.
This is provided for compatibility reasons, as well as to facilitate the migration
to RPy2.

:mod:`rpy2.interactive`
-----------------------

High-level interface, with an eye for interactive work. Largely based
on :mod:`rpy2.robjects` (See below).


:mod:`rpy2.robjects`
--------------------

Higher-level interface, when ease-of-use matters most.


:mod:`rpy2.rinterface`
----------------------

Low-level interface to R, when speed and flexibility
matter most. Here the programmer gets close(r) to R's C-level
API.

:mod:`rpy2.rlike`
-----------------

Data structures and functions to mimic some of R's features and specificities



Design notes
============


When designing rpy2, attention was given to make:

- the use of the module simple from both a Python or R user's perspective

- minimize the need for knowledge about R, and the need for tricks and workarounds.

- the possibility to customize a lot while remaining at the Python level (without having to go down to C-level).


:mod:`rpy2.robjects` implements an extension to the interface in
:mod:`rpy2.rinterface` by extending the classes for R
objects defined there with child classes.

The choice of inheritance was made to facilitate the implementation
of mostly inter-exchangeable classes between :mod:`rpy2.rinterface`
and :mod:`rpy2.robjects`. For example, an :class:`rpy2.rinterface.SexpClosure`
can be given any :class:`rpy2.robjects.RObject` as a parameter while
any :class:`rpy2.robjects.Function` can be given any
:class:`rpy2.rinterface.Sexp`. Because of R's functional basis,
a container-like extension is also present.

The module :mod:`rpy2.rpy_classic` is using delegation, letting us
demonstrate how to extend :mod:`rpy2.rinterface` with an alternative
to inheritance.


Acknowledgements
================

Acknowledgements go to the following individuals or group of individuals
for contributions, support, and early testing (by alphabetical order):

Alexander Belopolsky,
Brad Chapman,
Peter Cock,
Contributors,
Dirk Eddelbuettel,
JRI author(s),
Thomas Kluyver,
Walter Moreira, 
Numpy list responders,
Laurent Oget,
John Owens,
Nicolas Rapin,
R authors,
R-help list responders,
Grzegorz Slodkowicz,
Nathaniel Smith,
Gregory Warnes




    

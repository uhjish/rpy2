****************
Related projects
****************

Other interfaces
================

The `rtools <http://pypi.python.org/pypi/rtools>`_ package proposes
variations on the higher-level interface in rpy2.


Bioinformatics
==============

Cloud computing
---------------

`rpy2` is among the many bioinformatics-oriented packages
provided with `CloudBioLinux <http://cloudbiolinux.org/>`_. Check it out if
you are considering a project involving cloud computing.


Bioconductor
------------

Bioconductor is a popular set of R packages for bioinformatics.
A number of classes defined within that project are exposed as Python
classes through rpy2,
in the project `rpy2-bioconductor-extensions <http://pypi.python.org/pypi/rpy2-bioconductor-extensions/0.2-dev>`_. The bioconductor project is evolving quite rapidely the mapping might not longer be working.

The `blog of Brad Chapman <http://bcbio.wordpress.com/>`_ also has good examples about how to use `rpy2` for bioinformatics tasks (or Python for bioinformatics
in general).


.. _interactive-sessions:

Interactive consoles
====================

Data analysts often like to work interactively, that is going through short
cycles like:

* write a bit of code, which can be mostly involving a call to an existing function

* run that code

* inspect the results, often using plots and figures

R users will be particularly familiar with this sort of approach, and will likely
want it when working with :mod:`rpy2`.

Obviously the Python console can be used, but there exist improvements to it, making
the user experience more pleasant with features such as history and autocompletion.

ipython: interactive-python shell
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Developed under of the `scipy <http://scipy.org>` (Scientific Python) umbrella,
ipython has an "R magic" mode since its release 0.13.

Ipython has also a system of noteboks and a server backend,
very convenient for running R on remote servers. Check its
documentation. 

.. note::

   Historical note:
   
   The "R magic" bears similarities with the extension to rpy2 :mod:`rnumpy`,
   developped for rpy2-2.0.x series and seemingly unmaintained since then.

   More details on rnumpy can be found on the 
   `rnumpy page <http://bitbucket.org/njs/rnumpy/wiki/Home>`_



Other interactive environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* bpython: curse-based enhancement to the Python console

* emacs: the Emacs text editor can be used to host a python session, 
  or an ipython session


Embeddeding an R console
------------------------

Python can be used to develop full-fledged applications, including applications with
a graphical user interface. 

:mod:`rpy2` can be used to provide an R console embedded in such applications, 
or build an alternative R GUI.

When offering an R console, the developer(s) may want to retain control on the
the way interaction with R is handled, at the level of the console and for the
base R functions targetting interactivity (see Section  :ref:`rinterface-callbacks`).

The `RPyGTK project <http://code.google.com/p/rpygtk/>`_ demonstrates how
:mod:`rpy2` can be used to implement a full-blown GUI for R using python.


R-like data strucutures
=======================

R's data frames are extremely convient when manipulating data.
In :mod:`rpy2` the original R `data.frame` is represented by
:class:`rpy2.robjects.vectors.DataFrame`, but the
`pydataframe <http://code.google.com/p/pydataframe/>`_ project
has a pure Python implementation of them (with a compatibility
layer with :mod:`rpy2` providing a seamless transition
whenever needed.

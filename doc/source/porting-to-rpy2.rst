Porting code to rpy2
====================


From R
------

From rpy
--------

Compatibility layer
^^^^^^^^^^^^^^^^^^^

A compatibility layer exists, although it currently does not implement
completely the rpy interface.

From rpy2-2.0.x
---------------

This section refers to changes in the :mod:`rpy2.objects` layer.
If interested in changes to the lower level :mod:`rpy2.rinterface`,
the list of changes in the appendix should be consulted.

Camelcase
^^^^^^^^^

The camelCase naming disappeared from variables and methods, as it seemed
to be mostly absent from such obejcts in the standard library
(although nothing specific appears about that in :pep:`8`).

Practically, this means that `globalEnv` became `globalenv`, `baseEnv` became `baseenv`, etc...

R-prefixed class names
----------------------

Class names prefixed with the letter `R` were cleaned from that prefix.
For example, `RVector` became `Vector`, `RDataFrame` became `DataFrame`, etc...

Namespace for R packages
^^^^^^^^^^^^^^^^^^^^^^^^

The function :func:`rpy2.robjects.packages.importr` should be used to import an R package
name space as a Python-friendly object

>>> from rpy2.robjects.packages import importr
>>> base = importr("base")
>>> base.letters[0]
'a'

Whenever possible, this steps performs a safe 
conversion of '.' in R variable names into '_' for the Python variable
name.

Parameter names in function call
---------------------------------

By default, R fucntion exposed will have a safe translation of their parameter names
attempted ('.' will become '_')


Missing values
---------------

R has a built-in concept of *missing values*, and of types for missing values.
This now better integrated into rpy2

:ref:`missing_values`

Graphics
--------

The combined use of namespaces for R packages (see above),
and of custom representation of few specific R libraries is making
the generation of graphics (even) easier. 

:ref:`graphics`


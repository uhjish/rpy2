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

Faithful example
^^^^^^^^^^^^^^^^

In years, Tim Church's *Old faithful* example has reached an iconic
status for :mod:`rpy` users. We use it as a Rosetta stone and provide
its translation into :mod:`rpy2.robjects`.


Setting up:

.. code-block:: python

   from rpy2.robjects.vectors import DataFrame
   from rpy2.robjects.packages import importr

   r_base = importr('base')

Importing the data:

.. code-block:: python

   faithful_data = DataFrame.from_csvfile('faithful.dat', sep = " ")


Summary:

.. code-block:: python

   edsummary = r_base.summary(faithful_data.rx2("eruptions"))
   for k in edsummary.names:
      print("%s: %.3f\n" %(k, edsummary.r[k][0]))

Stem-and-leaf plot:

.. code-block:: python

   graphics = importr('graphics')

   print("Stem-and-leaf plot of Old Faithful eruption duration data")
   graphics.stem(faithful_data.rx2("eruptions"))

Histogram:

.. code-block:: python

   grdevices = importr('grDevices')

   grdevices.png('faithful_histogram.png', width = 733, height = 550)

   graphics.hist(ed, r.seq(1.6, 5.2, 0.2), 
                 prob = True, col = "lightblue",
                 main = "Old Faithful eruptions", xlab = "Eruption duration (seconds)")
   graphics.lines(r.density(ed,bw=0.1), col = "orange")
   graphics.rug(ed)
   grdevices.dev_off()

.. code-block:: python

   long_ed = robjects.FloatVector([x for x in ed if x > 3])
   grdevices.png('faithful_ecdf.png', width = 733, height = 550)

   stats = importr('stats')

   params = {'do.points' : False, 
              'verticals' : 1, 
              'main' : "Empirical cumulative distribution function of " + \
                       "Old Faithful eruptions longer than 3 seconds"}
   graphics.plot(r.ecdf(long_ed), **params)
   x = r_base.seq(3, 5.4, 0.01)
   graphics.lines(x, r_base.pnorm(x, mean = r.mean(long_ed), 
                                  sd = r_base.sqrt(r_base.var(long_ed))),
                  lty = 3, lwd = 2, col = "salmon")
   grdevices.dev_off()

.. code-block:: python
    
   grdevices.png('faithful_qq.png', width = 733, height = 550)
   r.par(pty="s")
   stats.qqnorm(long_ed,col="blue")
   graphics.qqline(long_ed,col="red")
   grdevices.dev_off()



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

Practically, this means that the following name changes occurred:

+----------------------+-------------+
| old name             | new name    |
+======================+=============+
| :mod:`rpy2.robjects`               |
+----------------------+-------------+
| `globalEnv`          | `globalenv` |
+----------------------+-------------+
| `baseNameSpaceEnv`   | `baseenv`   |
+----------------------+-------------+
| :mod:`rpy2.rinterface`             |
+----------------------+-------------+
| `globalEnv`          | `globalenv` |
+----------------------+-------------+
| `baseEnv`            | `baseenv`   |
+----------------------+-------------+


R-prefixed class names
----------------------

Class names prefixed with the letter `R` were cleaned from that prefix.
For example, `RVector` became `Vector`, `RDataFrame` became `DataFrame`, etc...

+---------------+--------------+
| old name      | new name     |
+===============+==============+
| :mod:`rpy2.robjects`         |
+---------------+--------------+
| `RVector`     | `Vector`     |
+---------------+--------------+
| `RArray`      | `Array`      |
+---------------+--------------+
| `RMatrix`     | `Matrix`     |
+---------------+--------------+
| `RDataFrame`  | `DataFrame`  |
+---------------+--------------+
| `REnvironment`| `Environment`|
+---------------+--------------+
| `RFunction`   | `Function`   |
+---------------+--------------+
| `RFormula`    | `Formula`    |
+---------------+--------------+


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

The documentation in Section :ref:`robjects-packages` gives more details.

Parameter names in function call
---------------------------------

By default, R functions exposed will have a safe translation of their named parameters
attempted ('.' will become '_'). Section :ref:`robjects-functions` should be checked for
details.


Missing values
---------------

R has a built-in concept of *missing values*, and of types for missing values.
This now better integrated into rpy2 (see Section :ref:`missing_values`)

Graphics
--------

The combined use of namespaces for R packages (see above),
and of custom representation of few specific R libraries is making
the generation of graphics (even) easier (see Section :ref:`graphics`).


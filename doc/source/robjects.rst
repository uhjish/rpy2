.. index::
   module: rpy2.robjects


*************
rpy2.robjects
*************

.. module:: rpy2.robjects
   :synopsis: High-level interface with R


Overview
========

This module is intended for casual and general use.
Its aim is to abstracts some of the details and provide an
intuitive interface to R.


>>> import rpy2.robjects as robjects


:mod:`rpy2.robjects` is written on the top of :mod:`rpy2.rinterface`, and one
not satisfied with it could easily build one's own flavor of a
Python-R interface by modifying it (:mod:`rpy2.rpy_classic` is an other
example of a Python interface built on the top of :mod:`rpy2.rinterface`).

Classes:

:class:`RObject`
  Parent class for R objects.

:class:`RVector`
  An R vector

:class:`REnvironment`
  An R environment.

:class:`RFunction`
  An R function.


Class R
=======

This class is currently a singleton, with
its one representation instanciated when the
module is loaded:

>>> robjects.r
>>> print(robjects.r)

The instance can be seen as the entry point to an
embedded R process, and the elements that would be accessible
from an equivalent R environment are accessible as attributes
of the instance.
Readers familiar with the ctypes module for Python will note
the similarity with ctypes.

R vectors:

>>> pi = robjects.r.pi
>>> letters = robjects.r.letters


R functions:

>>> plot = robjects.r.plot
>>> dir = robjects.r.dir

Just like it was the case with RPy-1.x, on-the-fly
evaluation of R code contained in a string can be performed
by calling the r instance:

>>> robjects.r('1:2')
3
>>> sqr = ro.r('function(x) x^2)
>>> sqr
function (x)
x^2
>>> sqr(2)
4

.. index::
   pair: robjects;RObject

R objects
=========

The class :class:`rpy2.robjects.RObject`
represents an arbitray R object, meaning than object
cannot be represented by any of the classes :class:`RVector`,
:class:`RFunction`, :class:`REnvironment`. 

The class inherits from the class
:class:`rpy2.rinterface.Sexp`.

.. index::
   pair: robjects;RVector

R vectors
=========

Beside functions, and environemnts, most of the objects
an R user is interacting with are vector-like.
For example, this means that any scalar is in fact a vector
of length one.

The class :class:`RVector` has a constructor:

>>> x = robjects.RVector(3)

The class inherits from the class
:class:`rpy2.rinterface.VectorSexp`.

Operators
---------

Mathematical operations on vectors: the following operations
are performed element-wise, recycling the shortest vector if
necessary.

+-------+---------+
| ``+`` | Add     |
+-------+---------+
| ``-`` | Subtract|
+-------+---------+
| ``*`` | Multiply|
+-------+---------+
| ``/`` | Divide  |
+-------+---------+

.. index::
   pair: RVector;indexing

Indexing
--------

Indexing can become a thorny issue, since Python indexing starts at zero
and R indexing starts at one.

The python :meth:`__getitem__` method behaves like a Python user would expect
it for a vector (and indexing starts at zero),
while the method :meth:`subset` behaves like a R user would expect it
(indexing starts at one, and a vector of integers, booleans, or strings can
be given to subset elements).

>>> x = robjects.r.seq(1, 10)
>>> x[0]
1
>>> x.subset(0)
integer(0)
>>> x.subset(1)
1L
>>> x.subset(-1)
2:10
>>> x.subset(True)
1:10

This class is using the class :class:`rinterface.SexpVector`, 
and its documentation can be referred to for details of what is happenening
at the low-level.


Numpy
-----

Vectors are understood as Numpy or Numeric arrays::

  import numpy
  ltr = robjects.r.letters
  ltr_np = numpy.array(ltr)

.. index::
   pair: robjects;REnvironment
   pair: robjects;globalEnv

R environments
==============

R environments can be described to the Python user as
an hybrid of a dictionary and a scope.

The first of all environments is called the Global Environment,
that can also be referred to as the R workspace.

>>> globalEnv = robjects.globalEnv


An R environment in RPy2 can be seen as a kind of Python
dictionnary.

Assigning a value to a symbol in an environment has been
made as simple as assigning a value to a key in a Python
dictionary:

>>> robjects.r.ls(globalEnv)
>>> globalEnv["a"] = 123
>>> robjects.r.ls(globalEnv)


Care must be taken when assigning objects into an environment
such as the Global Environment, as it can hide other objects
with an identical name.
For example:

>>> globalEnv["pi"] = 123
>>> robjects.r.pi
123L
>>>

>>> robjects.r.rm("pi")
>>> robjects.r.pi
3.1415926535897931

The class inherits from the class
:class:`rpy2.rinterface.SexpEnvironment`.


An environment is also iter-able, returning all the symbols
(keys) it contains:

>>> env = robjects.r.baseenv()
>>> len([x for x in env])

.. index::
   pair: robjects; RFunction
   pair: robjects; function

R functions
===========

>>> plot = robjects.r.plot
>>> rnorm = robjects.r.rnorm
>>> plot(rnorm(100), ylab="random")


The class inherits from the class
:class:`rpy2.rinterface.SexpClosure`.


Mapping between rpy2 objects and other python objects
=====================================================

The mapping between low-level objects is performed by the
functions XXX and XXX.

A developper can easily add his own mapping XXX.


Examples
========

The following section demonstrates some of the features of
rpy2 by the example. The wiki on the sourceforge website
will hopefully be used as a cookbook.


Example::

  import array

  r = robjects.r

  x = array.array('i', range(10))
  y = r.rnorm(10)

  r.X11()

  r.par(mfrow=array.array('i', [2,2]))
  r.plot(x, y, ylab="foo/bar", col="red")

  kwargs = {'ylab':"foo/bar", 'type':"b", 'col':"blue", 'log':"x"}
  r.plot(x, y, **kwargs)

Linear models
-------------

The R code is:

.. code-block:: r

   ctl <- c(4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14)
   trt <- c(4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69)
   group <- gl(2, 10, 20, labels = c("Ctl","Trt"))
   weight <- c(ctl, trt)

   anova(lm.D9 <- lm(weight ~ group))

   summary(lm.D90 <- lm(weight ~ group - 1))# omitting intercept

The :mod:`rpy2.robjects` code is

.. code-block:: python

   ctl = [4.17,5.58,5.18,6.11,4.50,4.61,5.17,4.53,5.33,5.14]
   trt = [4.81,4.17,4.41,3.59,5.87,3.83,6.03,4.89,4.32,4.69]
   group = r.gl(2, 10, 20, labels = ["Ctl","Trt"])
   weight = ctl + trt

   robjects.globalEnv["weight"] = weight
   robjects.globalEnv["group"] = group
   lm_D9 = r.lm("weight ~ group")
   r.anova(lm_D9)

   lm.D90 = r.lm("weight ~ group - 1"))
   summary(lm.D90)
   

Principal component analysis
----------------------------

The R code is

.. code-block:: r

  m <- matrix(rnorm(100), ncol=5)
  pca <- princomp(m)
  plot(pca, main="Eigen values")
  biplot(pca, main="biplot")

The :mod:`rpy2.robjects` code is

.. code-block:: python

  m = r.matrix(r.rnorm(100), ncol=5)
  pca = r.princomp(m)
  r.plot(pca, main="Eigen values")
  r.biplot(pca, main="biplot")
   


S4 classes
----------


.. code-block:: python

  if not r.require("GO")[0]:
      raise(Exception("Bioconductor Package GO missing"))

  goItem = r.GOTERM["GO:0000001"]


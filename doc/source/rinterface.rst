.. module:: rpy2.rinterface
   :platform: Unix, Windows
   :synopsis: Low-level interface with R



*******************
Low-level interface
*******************


Overview
========

The package :mod:`rinterface` is provided as a lower-level interface,
for situations where either the use-cases addressed by :mod:`robjects`
are not covered, or for the cases where the layer in :mod:`robjects`
has an excessive cost in terms of performance.

The package can be imported with:

>>> import rpy2.rinterface as rinterface


.. index::
   single: initialization

Initialization
--------------

One has to initialize R before much can be done.
The function :func:`initr` lets one initialize
the embedded R.

This is done with the function :meth:`initr`.


.. autofunction:: initr()


>>> rinterface.initr()

Initialization should only be performed once. 
To avoid unpredictable results when using the embedded R, 
subsequent calls to :func:`initr` will not have any effect.

The functions :func:`get_initoptions` and :func:`set_initoptions`
can be used to modify the options.
Default parameters for the initialization are otherwise
in the module variable `initoptions`.



.. index::
   single: initialize R_HOME

.. note::
   If calling :func:`initr` returns an error stating that
   :envvar:`R_HOME` is not defined, you should either have the :program:`R` executable in
   your path (:envvar:`PATH` on unix-alikes, or :envvar:`Path` on Microsoft Windows) or
   have the environment variable :envvar:`R_HOME` defined. 

Ending R
^^^^^^^^

Ending the R process is possible, but starting it again with
:func:`initr` does appear to lead to an R process that is hardly usable.
For that reason, the use of :func:`endEmbeddedR` should be considered
carefully, if at all.

R space and Python space
------------------------

When using the RPy2 package, two realms are co-existing: R and Python.

The :class:`Sexp_Type` objects can be considered as Python envelopes pointing
to data stored and administered in the R space.

R variables are existing within an embedded R workspace, and can be accessed
from Python through their python object representations.

We distinguish two kind of R objects: named objects and anonymous objects. 
Named objects have an associated symbol in the R workspace.

Named objects
^^^^^^^^^^^^^

For example, the following R code is creating two objects, named `x` and `hyp`
respectively, in the `global environment`.
Those two objects could be accessed from Python using their names.

.. code-block:: r

   x <- c(1,2,3)

   hyp <- function(x, y) sqrt(x^2 + y^2)

Two environments are provided as :class:`rpy2.rinterface.SexpEnvironment`

.. index::
   single: globalenv
   single: SexpEnvironment; globalenv

.. rubric:: globalenv

The global environment can be seen as the root (or topmost) environment,
and is in fact a list, that is a sequence, of environments.

When an R library (package in R's terminology) is loaded,
is it added to the existing sequence of environments. Unless
specified, it is inserted in second position. The first position
being always attributed to the global environment.
The library is said to be attached to the current search path.

.. index::
   pair: rinterface; baseenv
   single: SexpEnvironment; baseenv

.. rubric:: baseenv

The base package has a namespace, that can be accessed as an environment.

.. note::
   Depending on what is in `globalenv` and on the attached packages, base
   objects can be masked when starting the search from `globalenv`. 
   Use `baseenv`
   when you want to be sure to access a function you know to be
   in the base namespace.


Anonymous objects
^^^^^^^^^^^^^^^^^

Anonymous R objects do not have an associated symbol, yet are protected
from garbage collection.

Such objects can be created when using the constructor for an `Sexp*` class.

For example:

>>> x = rinterface.IntVector((1,2,3))

creates a fully usable R vector, but it does not have an associtated
R symbol (it is in memory, but cannot be called by name). It is will be
protected from garbage collection until the Python garbage collector
claims it.


Pass-by-value paradigm
----------------------

The root of the R language is functional, with arguments passed by value.
R is actually using tricks to lower memory usage, such as only copying an object
when needed (that is when the object is modified in a local block),
but copies of objects are nevertheless frequent. This can remain unnoticed
by a user until large objects are in use or a large number of modification
of objects are performed, in which case performance issues may appear.
An infamous example is when the column names for a matrix are changed,
bringing a system to its knees when the matrix is very large, 
as the whole matrix ends up being copied. 

On the contrary, Python is using pointer objects passed around
through function calls, and since :mod:`rpy2`, is a Python-to-R interface
the Python approach was conserved.

Although being contrived, the example below will illustrate the point.
With R, renaming a column is like:

.. code-block:: r

   # create a matrix
   m <- matrix(1:10, nrow = 2,
               dimnames = list(c("1", "2"),
	                       c("a", "b", "c", "d", "e")))
   # rename the third column
   i <- 3
   colnames(m)[i] <- "foo"

With :mod:`rpy2.rinterface`:
   
.. code-block:: python

   # import and initialize
   import rpy2.rinterface as ri
   ri.initr()

   # make a function to rename column i
   def rename_col_i(m, i, name):
       m.do_slot("dimnames")[1][i] = name

   # create a matrix
   matrix = ri.baseenv["matrix"]
   rlist = ri.baseenv["list"]
   m = matrix(ri.baseenv[":"](1, 10),
              nrow = 2,
              dimnames = rlist(ri.StrSexpVector(("1", "2")),
	                       ri.StrSexpVector(("a", "b", "c", "d", "e"))))

Now we can check that the column names

>>> tuple(m.do_slot("dimnames")[1])
('a', 'b', 'c', 'd', 'e')

And rename the third column (remembering that R vectors are 1-indexed
while Python sequences are 0-indexed).

>>> i = 3-1   
>>> rename_col_i(m, i, ri.StrSexpVector(("foo", )))
>>> tuple(m.do_slot("dimnames")[1])
('a', 'b', 'foo', 'd', 'e')

Unlike with the R code, neither the matrix or the vector with the column names
are copied. Whenever this is not a good thing, R objects can be copied the
way Python objects are usually copied (using :func:`copy.deepcopy`,
:class:`Sexp` implements :meth:`Sexp.__deepcopy__`).

Memory management and garbage collection
----------------------------------------

Whenever the pass-by-value paradigm is applied stricly,
garbage collection is straightforward as objects only live within
the scope they are declared, but R is using a slight modification
of this in order to minimize memory usage. Each R object has an
attribute :attr:`Sexp.named` attached to it, indicating
the need to copy the object.

>>> import rpy2.rinterface as ri
>>> ri.initr()
0
>>> ri.baseenv['letters'].named
0

Now we assign the vector *letters* in the R base namespace
to a variable *mine* in the R globalenv namespace:

>>> ri.baseenv['assign'](ri.StrSexpVector(("mine", )), ri.baseenv['letters'])
<rpy2.rinterface.SexpVector - Python:0xb77ad280 / R:0xa23c5c0>
>>> tuple(ri.globalenv)
("mine", )
>>> ri.globalenv["mine"].named
2

The *named* is 2 to indicate that *mine* should be copied if a modication
of any sort is performed on the object.

Parsing and evaluating R code
-----------------------------

The R C-level function for parsing an arbitrary string a R code is exposed
as the function :func:`parse`

>>> expression = ri.parse('1 + 2')

The resulting expression is a nested list of R statements.

>>> len(expression)
1
>>> len(expression[0])
3

The R code *1 + 2* translates to an expression of length 3:
*+(1, 2)*, that is a call to the function *+* (or rather the symbol associated
with the function) with the arguments *1* and *2*. 
 
>>> ri.str_typeint(expression[0][0].typeof)
'SYMSXP'
>>> tuple(expression[0][1])
(1.0,)
>>> tuple(expression[0][2])
(2.0,)



.. note ::

   The expression must be evaluated if the result from its execution
   is wanted.


.. autofunction:: parse()


Calling Python functions from R
-------------------------------

As could be expected from R's functional roots,
functions are first-class objects.
This means that the use of higher-order functions is not seldom,
and this also means that the Python programmer has to either
be able write R code for functions as arguments, or have a way
to pass Python functions to R as genuine R functions. 
That last options is becoming possible, in other words one can
write a Python function and expose it to R in such a way that
the embedded R engine can use as a regular R function.

As an example, let's consider the R function 
*optim()* that looks for optimal parameters for a given cost function.
The cost function should be passed in the call to *optim()* as it will be
repeatedly called as the parameter space is explored, and only Python
coding skills are necessary as the code below demonstrates it.

.. code-block:: python

   from rpy2.robjects.vectors import FloatVector
   from rpy2.robjects.packages import importr
   import rpy2.rinterface as ri
   stats = importr('stats')
   
   # Rosenbrock Banana function as a cost function
   # (as in the R man page for optim())
   def cost_f(x):
       x1 = x[0]
       x2 = x[1]
       return 100 * (x2 - x1 * x1)**2 + (1 - x1)**2

   # wrap the function f so it can be exposed to R
   cost_fr = ri.rternalize(cost_f)

   # starting parameters
   start_params = FloatVector((-1.2, 1))

   # call R's optim()
   res = stats.optim(start_params, cost_fr)

For convenience, the code examples uses the higher-level interface
robjects whenever possible.

The lower-level function :func:`rternalize` will take an arbitray
Python function and return an :class:`rinterface.SexpClosure` instance,
that is a object that can be used by R as a function.


.. autofunction:: rternalize()

Interactive features
====================

The embedded R started from :mod:`rpy2` is interactive by default, which 
means that a number of interactive features present when working
in an interactive R console will be available for use.

Such features can be called explicitly by the :mod:`rpy2` user, but
can also be triggered indirectly, as some on the R functions will behave
differently when run interactively compared to when run in the so-called
*BATCH mode*.

.. note::

   However, interactive use may mean the ability to periodically check
   and process events. This is for example the case with interactive
   graphics devices or with the HTML-based help system 
   (see :ref:`rinterface-interactive-processevents`).


I/O with the R console
----------------------

See :ref:`rinterface-callbacks_consoleio`.


.. _rinterface-interactive-processevents:

Processing interactive events
-----------------------------

An interactive R session is can start interactive activities
that require a continuous monitoring for events. A typical example
is the interactive graphical devices (`plotting windows`),
as they can be resized and the information they display is refreshed.

However, to do so the R process must be instructed to process
pending interactive events. This is done by the R console for example,
but :mod:`rpy2` is designed as a library rather than a threaded R process
running within Python (yet this can be done as shown below).

The way to restore interactivity this is simply to call the function
:func:`rinterface.process_revents` at regular intervals.

This can be taken care of by an higher-level interface, or can
be hacked quickly as::

   import rpy2.rinterface as rinterface
   import time

   def r_refresh(interval = 0.03):
       # Ctrl-C to interrupt
       while True:
           rinterface.process_revents()
           time.sleep(interval)

The module :mod:`threading` offers a trivial way to dispatch the work
to a thread whenever a script is running::

   import threading
   
   t = threading.Timer(0.1, r_refresh)
   t.start()

By doing so, one makes R run an thread with the Python process.

   
.. autofunction:: process_revents()


Classes
=======


:class:`Sexp`
-------------

The class :class:`Sexp` is the base class for all R objects.


.. class:: Sexp

   .. attribute:: __sexp__

      Opaque C pointer to the underlying R object

   .. attribute:: named

      `R` does not count references for its object. This method
      returns the `NAMED` value (an integer). 
      See the R-extensions manual for further details.

   .. attribute:: typeof

      Internal R type for the underlying R object

      .. doctest::

         >>> letters.typeof
         16

   .. method:: __deepcopy__(self)

      Make a *deep* copy of the object, calling the R-API C function
      c:function::`Rf_duplicate()` for copying the R object wrapped.

      .. versionadded:: 2.0.3

   .. method:: do_slot(name)

      R objects can be given attributes. In R, the function
      *attr* lets one access an object's attribute; it is
      called :meth:`do_slot` in the C interface to R. 

      :param name: string
      :rtype: instance of :class:`Sexp`

      >>> matrix = rinterface.globalenv.get("matrix")
      >>> letters = rinterface.globalenv.get("letters")
      >>> m = matrix(letters, ncol = 2)
      >>> [x for x in m.do_slot("dim")]
      [13, 2]
      >>>

   .. method:: do_slot_assign(name, value)

      Assign value to the slot with the given name, creating the slot whenver
      not already existing.

      :param name: string
      :param value: instance of :class:`Sexp`


   .. method:: rsame(sexp_obj)

      Tell whether the underlying R object for sexp_obj is the same or not.

      :rtype: boolean


.. .. autoclass:: rpy2.rinterface.Sexp
..   :members:



.. index::
   single: SexpVector
   single: rinterface; SexpVector


:class:`SexpVector`
-------------------

Overview
^^^^^^^^

In R all scalars are in fact vectors.
Anything like a one-value variable is a vector of
length 1.

To use again the constant *pi*:

>>> pi = rinterface.globalenv.get("pi")
>>> len(pi)
1
>>> pi
<rinterface.SexpVector - Python:0x2b20325d2660 / R:0x16d5248>
>>> pi[0]
3.1415926535897931
>>>

The letters of the (western) alphabet are:

>>> letters = rinterface.globalenv.get("letters") 
>>> len(letters)
26
>>> LETTERS = rinterface.globalenv.get("LETTERS") 


R types
^^^^^^^

R vectors all have a `type`, sometimes referred to in R as a `mode`.
This information is encoded as an integer by R, but it can sometimes be
better for human reader to be able to provide a string.

.. function:: str_typeint(typeint)

   Return a string corresponding to a integer-encoded R type.

   :param typeint: integer (as returned by :attr:`Sexp.typeof`)
   :rtype: string


.. index::
   pair: rinterface;indexing

Indexing
^^^^^^^^

The indexing is working like it would on regular `Python`
tuples or lists.
The indexing starts at 0 (zero), which differs from `R`, 
where indexing start at 1 (one).

.. note::
   The *__getitem__* operator *[*
   is returning a Python scalar. Casting
   an *SexpVector* into a list is only a matter 
   of either iterating through it, or simply calling
   the constructor :func:`list`.


Common attributes
^^^^^^^^^^^^^^^^^

.. index::
   single: names;rinterface

.. rubric:: Names


In R, vectors can be named, that is each value in the vector
can be given a name (that is be associated a string).
The names are added to the other as an attribute (conveniently
called `names`), and can be accessed as such:

>>> options = rinterface.globalenv.get("options")()
>>> option_names = options.do_slot("names")
>>> [x for x in options_names]

.. note::
   Elements in a name vector do not have to be unique. A Python
   counterpart is provided as :class:`rpy2.rlike.container.TaggedList`.

.. index::
   single: dim
   single: dimnames


.. rubric:: Dim and dimnames

In the case of an `array`, the names across the
respective dimensions of the object are accessible
through the slot named `dimnames`.


.. index::
   single: missing values

.. rubric:: Missing values

.. _missing_values:

.. note::

   R also has the notion of missing parameters in function calls.
   This is a separate concept, and more information about are given in 
   Section :ref:`rinterface-functions`.

In R missing the symbol *NA* represents a missing value.
The general rule that R scalars are in fact vectors applies here again,
and the following R code is creating a vector of length 1.

.. code-block:: r

   x <- NA

The type of NA is logical (boolean), and one can specify a different
type with the symbols
*NA_character_*, *NA_integer_*, *NA_real_*, and *NA_complex_*.

In :mod:`rpy2.rinterface`, the symbols can be accessed by through 
:data:`NA_Character`, 
:data:`NA_Integer`, 
:data:`NA_Real`.

Those are singleton instance from respective *NA<something>Type* classes.

>>> my_naint = rinterface.NAIntegerType()
>>> my_naint is rinterface.NA_Integer
True
>>> my_naint == rinterface.NA_Integer
True

*NA* values can be present in vectors returned by R functions.

>>> rinterface.baseenv['as.integer'](rinterface.StrSexpVector(("foo",)))[0]
NA_integer_

*NA* values can have operators implemented, but the results will then
be missing values.
 
>>> rinterface.NA_Integer + 1
NA_integer_
>>> rinterface.NA_Integer * 10
NA_integer_

.. warning::

   Python functions relying on C-level implementations might not be following
   the same rule for *NAs*.
   
   >>> x = rinterface.IntSexpVector((1, rinterface.NA_Integer, 2))
   >>> sum(x)
   3
   >>> max(x)
   2
   >>> min(x)
   NA_integer_


This should be preferred way to use R's NA as those symbol are little
peculiar and cannot be retrieved with :meth:`SexpEnvironment.get`.

Those missing values can also be used with the :mod:`rpy2.robjects` layer
and more documentation about their usage can be found there
(see :ref:`robjects-missingvalues`).

.. autoclass:: rpy2.rinterface.NAIntegerType()
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.NARealType()
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.NALogicalType()
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.NACharacterType()
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.NAComplexType()
   :show-inheritance:
   :members:


.. rubric:: Constructors

.. autoclass:: rpy2.rinterface.SexpVector(obj, sexptype, copy)
   :show-inheritance:
   :members:


Convenience classes are provided to create vectors of a given type:

.. autoclass:: rpy2.rinterface.StrSexpVector
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.IntSexpVector
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.FloatSexpVector
   :show-inheritance:
   :members:

.. autoclass:: rpy2.rinterface.BoolSexpVector
   :show-inheritance:
   :members:

.. index::
   single: SexpEnvironment
   single: rinterface; SexpEnvironment

.. _rinterface-sexpenvironment:

:class:`SexpEnvironment`
------------------------



:meth:`__getitem__` / :meth:`__setitem__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The *[* operator will only look for a symbol in the environment
without looking further in the path of enclosing environments.

The following will return an exception :class:`LookupError`:

>>> rinterface.globalenv["pi"]

The constant *pi* is defined in R's *base* package,
and therefore cannot be found in the Global Environment.

The assignment of a value to a symbol in an environment is as
simple as assigning a value to a key in a Python dictionary:

>>> x = rinterface.IntSexpVector([123, ])
>>> rinterface.globalenv["x"] = x


.. note::
   Not all R environment are hash tables, and this may
   influence performances when doing repeated lookups

.. note::
  a copy of the R object is made in the R space.

:meth:`__iter__`
^^^^^^^^^^^^^^^^

The object is made iter-able.

For example, we take the base name space (that is the environment
that contains R's base objects:

>>> base = rinterface.baseenv
>>> basetypes = [x.typeof for x in base]


.. warning::

   In the current implementation the content of the environment
   is evaluated only once, when the iterator is created. Adding 
   or removing elements to the environment will not update the iterator
   (this is a problem, that will be solved in the near future).


:meth:`get`
^^^^^^^^^^^

Whenever a search for a symbol is performed, the whole
search path is considered: the environments in the list
are inspected in sequence and the value for the first symbol found
matching is returned.

Let's start with an example:

>>> rinterface.globalenv.get("pi")[0]
3.1415926535897931

The constant `pi` is defined in the package `base`, that
is always in the search path (and in the last position, as it is
attached first). The call to :meth:`get` will
look for `pi` first in `globalenv`, then in the next environment
in the search path and repeat this until an object is found or the
sequence of environments to explore is exhausted.

We know that `pi` is in the base namespace and we could have gotten
here directly from there:

>>> ri.baseenv.get("pi")[0]
3.1415926535897931
>>> ri.baseenv["pi"][0]
3.1415926535897931
>>> ri.globalenv["pi"][0]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
LookupError: 'pi' not found

`R` can look specifically for functions, which is happening when
a parsed function call is evaluated.
The following example of an `R` interactive session should demonstrate it:

.. code-block:: r

   > mydate <- "hohoho"
   > mydate()
   Error: could not find function "mydate"
   >
   > date <- "hohoho"
   > date()
   [1] "Sat Aug  9 15:27:40 2008"

The base function `date` is still found, although a non-function object
is present earlier on the search path.

The same behavior can be obtained from :mod:`rpy2`
with the optional parameter `wantfun` (specify that :meth:`get`
should return an R function).

>>> ri.globalenv["date"] = ri.StrSexpVector(["hohoho", ])
>>> ri.globalenv.get("date")[0]
'hohoho'
>>> ri.globalenv.get("date", wantfun=True)
<rinterface.SexpClosure - Python:0x7f142aa96198 / R:0x16e9500>
>>> date = ri.globalenv.get("date", wantfun=True)
>>> date()[0]
'Sat Aug  9 15:48:42 2008'


R packages as environments
^^^^^^^^^^^^^^^^^^^^^^^^^^

In a `Python` programmer's perspective, it would be nice to map loaded `R`
packages as modules and provide access to `R` objects in packages the
same way than `Python` object in modules are accessed.

This is unfortunately not possible in a completely
robust way: the dot character `.`
can be used for symbol names in R (like pretty much any character), and
this can make an exact correspondance between `R` and `Python` names 
rather difficult.
:mod:`rpy` uses transformation functions that translates '.' to '_' and back,
but this can lead to complications since '_' can also be used for R symbols 
(although this is the approach taken for the high-level interface, see
Section :ref:`robjects-packages`).

There is a way to provide explict access to object in R packages, since
loaded packages can be considered as environments. To make it convenient
to use, one can consider making a function such as the one below:

.. code-block:: python

   def rimport(packname):
       """ import an R package and return its environment """
       as_environment = rinterface.baseenv['as.environment']
       require = rinterface.baseenv['require']
       require(rinterface.StrSexpVector(packname), 
               quiet = rinterface.BoolSexpVector((True, )))
       packname = rinterface.StrSexpVector(('package:' + str(packname)))
       pack_env = as_environment(packname)
       return pack_env

>>> class_env = rimport("class")
>>> class_env['knn']


For example, we can reimplement in `Python` the `R` function 
returning the search path (`search`).

.. code-block:: python

   def rsearch():
       """ Return a list of package environments corresponding to the
       R search path. """
       spath = [ri.globalenv, ]
       item = ri.globalenv.enclos()
       while not item.rsame(ri.emptyenv):
           spath.append(item)
	   item = item.enclos()
       spath.append(ri.baseenv)
       return spath


As an other example, one can implement simply a function that
returns from which environment an object called by :meth:`get` comes
from.

.. code-block:: python

   def wherefrom(name, startenv=ri.globalenv):
       """ when calling 'get', where the R object is coming from. """
       env = startenv
       obj = None
       retry = True
       while retry:
           try:
               obj = env[name]
               retry = False
           except LookupError, knf:
               env = env.enclos()
	       if env.rsame(ri.emptyenv):
                   retry = False
               else:
                   retry = True
       return env       


>>> wherefrom('plot').do_slot('name')[0]
'package:graphics'
>>> wherefrom('help').do_slot('name')[0]
'package:utils'

.. note::
   Unfortunately this does not generalize to all cases: the base package does not have a name.

   >>> wherefrom('get').do_slot('name')[0]
   Traceback (most recent call last):
   File "<stdin>", line 1, in <module>
   LookupError: The object has no such attribute.


.. index::
   single: closure
   single: SexpClosure
   single: rinterface; SexpClosure
   pair: rinterface; function


.. _rinterface-functions:

Functions
---------



.. rubric:: A function with a context

In R terminology, a closure is a function (with its enclosing
environment). That enclosing environment can be thought of as
a context to the function.

.. note::

   Technically, the class :class:`SexpClosure` corresponds to the R
   types CLOSXP, BUILTINSXP, and SPECIALSXP, with only the first one
   (CLOSXP) being a closure.

>>> sum = rinterface.globalenv.get("sum")
>>> x = rinterface.IntSexpVector([1,2,3])
>>> s = sum(x)
>>> s[0]
6

.. rubric:: Named arguments

Named arguments to an R function can be specified just the way
they would be with any other regular Python function.

>>> rnorm = rinterface.globalenv.get("rnorm")
>>> rnorm(rinterface.IntSexpVector([1, ]), 
          mean = rinterface.IntSexpVector([2, ]))[0]
0.32796768001636134

There are however frequent names for R parameters causing problems: all the names with a *dot*. using such parameters for an R function will either require
to:

* use the special syntax `**kwargs` on a dictionary with the named parameters

* use the method :meth:`rcall`.  


.. Index::
   single: rcall; order of parameters

.. rubric:: Order for named parameters

One point where function calls in R can differ from the ones in 
Python is that
all parameters in R are passed in the order they are in the call
(no matter whether the parameter is named or not),
while in Python only parameters without a name are passed in order.
Using the class :class:`OrdDict` in the module :mod:`rpy2.rlike.container`,
together with the method :meth:`rcall`,
permits calling a function the same way it would in R. For example::

   import rpy2.rlike.container as rpc
   args = rpc.OrdDict()
   args['x'] = rinterface.IntSexpVector([1,2,3])
   args[None] = rinterface.IntSexpVector([4,5])
   args['y'] = rinterface.IntSexpVector([6, ])
   rlist = rinterface.baseenv['list']
   rl = rlist.rcall(args.items())

>>> [x for x in rl.do_slot("names")]
['x', '', 'y']

.. index::
   single: closureEnv

.. rubric:: closureEnv

In the example below, we inspect the environment for the
function *plot*, that is the namespace for the
package *graphics*.

>>> plot = rinterface.globalenv.get("plot")
>>> ls = rinterface.globalenv.get("ls")
>>> envplot_list = ls(plot.closureEnv())
>>> [x for x in envplot_ls]
>>>


.. rubric:: Missing parameters

In R function calls can contain explicitely missing parameters.

.. code-block:: rconsole

   > sum(1,,3)
   Error: element 2 is empty;
      the part of the args list of 'sum' being evaluated was:
      (1, , 3)

This is used when extracting a subset of an array, with a missing
parameter interpreted by the extract function `[` like all elements
across that dimension must be taken.

.. code-block:: r

   m <- matrix(1:10, nrow = 5, ncol = 2)

   # extract the second column
   n <- m[, 2]

   # can also be written
   n <- "["(m, , 2)

:data:`rinterface.MissingArg` is a pointer to the singleton :class:`rinterface.MissingArgType`,
allowing to explicitly pass missing parameters to a function call.

For example, the extraction of the second column of a matrix with R shown above,
will write almost identically in rpy2.

.. code-block:: python

   import rpy2.rinterface as ri
   ri.initr()

   matrix = ri.baseenv['matrix']
   extract = ri.baseenv['[']

   m = matrix(ri.IntSexpVector(range(1, 11)), nrow = 5, ncol = 2)

   n = extract(m, ri.MissingArg, 2)


:class:`SexpS4`
---------------

Object-Oriented programming in R exists in several flavours, and one
of those is called `S4`.
It has its own type at R's C-API level, and because of that specificity
we defined a class. Beside that, the class does not provide much specific
features (see the pydoc for the class below). 

An instance's attributes can be accessed through the parent
class :class:`Sexp` method
:meth:`do_slot`.

.. autoclass:: rpy2.rinterface.SexpS4(obj)
   :show-inheritance:
   :members:

:class:`SexpExtPtr`
-------------------

External pointers are intended to facilitate the handling of C or C++ data structures
from R. In few words they are pointers to structures *external* to R. They have
been used to implement vectors and arrays in shared memory, or storage-based vectors
and arrays.

External pointers also do not obey the pass-by-value rule and can represent a way
to implement pointers in R.


Let us consider the following simple example:

.. code-block:: python
   
   ep = rinterface.SexpExtPtr("hohoho")

The Python string is now encapsulated into an R external pointer, and visible as such
by the embedded R process.

When thinking of sharing C-level structures between R and Python more involved examples
can be considered (here still a simple example):

.. code-block:: python

   import ctypes
   class Point2D(ctypes.Structure):
       _fields_ = [("x", ctypes.c_int),
                   ("y", ctypes.c_int)]

   pt = Point2D()

   ep = rinterface.SexpExtPtr(pt)


However, this remains a rather academic exercise unless there exists a way to access the
data from R; when used in R packages, external pointers have companion functions to
manipulate the C-level data structures.

In the case of external pointers and their companion functions and methods
defined by R packages, the rpy2 interface lets a programmer create such external pointers
directly from Python, using :mod:`ctypes` for example.

However, the rpy2 interface allows more than that since a programmer is able to make
a Python function accessible to R has is was a function of its own. It is possible
to define arbitrary Python data structures as well as functions or methods to operate
on them, pass the data structure to R as an external pointer, and expose the functions
and methods to R. 

.. autoclass:: rpy2.rinterface.SexpExtPtr(obj)
   :show-inheritance:
   :members:

Class diagram
=============

.. inheritance-diagram:: rpy2.rinterface


Misc. variables
===============

.. index::
   single: R_LEN_T_MAX
   single: R_HOME
   single: TRUE
   single: FALSE


R_HOME
  R HOME

:const:`R_LEN_T_MAX`
  largest usable integer for indexing R vectors

:const:`TRUE`/:const:`FALSE`
  R's TRUE and FALSE

.. index::
   single: CPLXSXP
   single: type; CPLXSXP
   single: ENVSXP
   single: type; ENVSXP
   single: INTSXP
   single: type; INTSXP
   single: LANGSXP
   single: type; LANGSXP
   single: LGLSXP
   single: type; LGLSXP
   single: STRSXP
   single: type; STRSXP
   single: REALSXP
   single: type; REALSXP
   single: RAWSXP
   single: type; RAWSXP

R types
-------

Vector types
^^^^^^^^^^^^

:const:`CPLXSXP`
  Complex 

:const:`INTSXP`
  Integer.

:const:`LGLSXP`
  Boolean (logical in the R terminology)

:const:`RAWSXP`
  Raw (bytes) value

:const:`REALSXP`
  Numerical value (float / double)

:const:`STRSXP`
  String

:const:`VECSXP`
  List

:const:`LISTSXP`
  Paired list

:const:`LANGSXP`
  Language object.

:const:`EXPRSXP`
  Unevaluated expression.

Function types
^^^^^^^^^^^^^^

:const:`CLOSXP`
  Function with an enclosure. Represented by :class:`rpy2.rinterface.SexpClosure`.

:const:`BUILTINSXP`
  Base function

:const:`SPECIALSXP`
  Some other kind of function

Other types
^^^^^^^^^^^

:const:`ENVSXP`
  Environment. Represented by :class:`rpy2.rinterface.SexpEnvironment`.

:const:`S4SXP`
  Instance of class S4. Represented by :class:`rpy2.rinterface.SexpS4`.


Types one should not meet
^^^^^^^^^^^^^^^^^^^^^^^^^

:const:`PROMSXP`
  Promise.


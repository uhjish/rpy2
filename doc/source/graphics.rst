********
Graphics
********

Introduction
============

This section shows how to make R graphics from rpy2, 
using some of the different graphics systems available to R users.

The purpose of this section is to get users going, and be able to figure out
by reading the R documentation how to perform the same plot in rpy2.


.. module:: rpy2.robjects.lib.grdevices
   :platform: Unix, Windows
   :synopsis: High-level interface with R

Graphical devices
-----------------

With `R`, all graphics are plotted into a so-called graphical device.
Graphical devices can be interactive, like for example `X11`, 
or non-interactive, like `png` or `pdf`. Non-interactive devices
appear to be files.

By default an interactive R session will open an interactive device
when needing one. If a non-interactive graphical device is needed,
one will have to specify it.

.. note::

   Do not forget to close a non-interactive device when done.
   This can be required to flush pending data from the buffer.


The module :mod:`grdevices` aims at representing the R package
*grDevices*.

.. code-block:: python

   import rpy2.robjects.lib.grdevices as grdevices

   grdevices.png(file="path/to/file.png", width=512, height=512)
   # plotting code here   
   grdevices.dev_off()


The package contains an :class:`REnvironment` :data:`grdevices_env` that
can be used to access an object known to belong to that R packages, e.g.:

>>> palette = grdevices.palette()
>>> print(palette)
[1] "black"   "red"     "green3"  "blue"    "cyan"    "magenta" "yellow" 
[8] "gray"




Getting ready
-------------

To run examples in this section we first import
:mod:`rpy2.robjects` and define few helper
functions.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- setup-begin
   :end-before: #-- setup-end


Package *lattice*
=================


Introduction
------------


Importing the package `lattice` is done the
same as it is done for other R packages.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- setuplattice-begin
   :end-before: #-- setuplattice-end


Scatter plot
------------

We use the dataset *mtcars*, and will use
the lattice function *xyplot* to make scatter plots.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- setupxyplot-begin
   :end-before: #-- setupxyplot-end


Lattice is working with formulae (see :ref:`robjects-formula`),
therefore we build one and store values in its environment.
Making a plot is then a matter of calling
the function *xyplot* with the *formula* as
as an argument.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- xyplot1-begin
   :end-before: #-- xyplot1-end


.. image:: _static/graphics_lattice_xyplot_1.png
   :scale: 50


The display of group information can be done
simply by using the named parameter groups.
This will indicate the different groups by
color-coding.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- xyplot2-begin
   :end-before: #-- xyplot2-end


.. image:: _static/graphics_lattice_xyplot_2.png
   :scale: 50

An alternative to color-coding is to have 
points is different *panels*. In lattice,
this done by specifying it in the formula.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- xyplot3-begin
   :end-before: #-- xyplot3-end


.. image:: _static/graphics_lattice_xyplot_3.png
   :scale: 50


.. module:: rpy2.robjects.lib.ggplot2
   :platform: Unix, Windows
   :synopsis: High-level interface with R


Package *ggplot2*
=================

Introduction
------------

The R package *ggplot2* is expected to be installed in the *R*
used from *rpy2*.

Here again, having data in a :class:`RDataFrame` is expected
(see :ref:`robjects-dataframes` for more information on such objects).

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- setupggplot2-begin
   :end-before: #-- setupggplot2-end


Plot
----


.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2mtcars-begin
   :end-before: #-- ggplot2mtcars-end


.. image:: _static/graphics_ggplot2mtcars.png
   :scale: 50

Aesthethics mapping
^^^^^^^^^^^^^^^^^^^

An important concept for the grammar of graphics is the
mapping of variables, or columns in a data frame, to
graphical representations.

Like it was shown for *lattice*, a third variable can be represented
on the same plot using color encoding, and this is now done by
specifying that as a mapping (the parameter *col* when calling
the :class:`Aes`):

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2mtcarscolcyl-begin
   :end-before: #-- ggplot2mtcarscolcyl-end
   
.. image:: _static/graphics_ggplot2mtcarscolcyl.png
   :scale: 50

The size of the graphical symbols plotted (here circular dots) can
also be mapped to a variable:

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2aescolsize-begin
   :end-before: #-- ggplot2aescolsize-end
   
.. image:: _static/graphics_ggplot2aescolsize.png
   :scale: 50


Geometry
^^^^^^^^

The *geometry* is how the data are represented. So far we used a scatter
plot of points, but there are other ways to represent our data.


.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2geombin2d-begin
   :end-before: #-- ggplot2geombin2d-end
   
.. image:: _static/graphics_ggplot2geombin2d.png
   :scale: 50


.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2geomboxplot-begin
   :end-before: #-- ggplot2geomboxplot-end
   
.. image:: _static/graphics_ggplot2geomboxplot.png
   :scale: 50

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2geomhistogram-begin
   :end-before: #-- ggplot2geomhistogram-end
   
.. image:: _static/graphics_ggplot2geomhistogram.png
   :scale: 50

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2geomhistogramfillcyl-begin
   :end-before: #-- ggplot2geomhistogramfillcyl-end
   
.. image:: _static/graphics_ggplot2geomhistogramfillcyl.png
   :scale: 50


.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2aescolboxplot-begin
   :end-before: #-- ggplot2aescolboxplot-end
   
.. image:: _static/graphics_ggplot2aescolboxplot.png
   :scale: 50


Models fitted to the data are also easy to add to a plot:

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2addsmooth-begin
   :end-before: #-- ggplot2addsmooth-end

   
.. image:: _static/graphics_ggplot2addsmooth.png
   :scale: 50

The *method* can be one of {*glm*, *gam*, *loess*, and *rlm*}.


.. image:: _static/graphics_ggplot2addsmoothmethods.png
   :scale: 50


The constructor for :class:`GeomSmooth` also accepts a parameter
*groupr*` that indicates if the fit should be done according to groups.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2smoothbycyl-begin
   :end-before: #-- ggplot2smoothbycyl-end
   
.. image:: _static/graphics_ggplot2smoothbycyl.png
   :scale: 50



Encoding the information in the column *cyl* is again
only a matter of specifying it in the :class:`AES` mapping.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2smoothbycylwithcolours-begin
   :end-before: #-- ggplot2smoothbycylwithcolours-end

   
.. image:: _static/graphics_ggplot2_smoothbycylwithcolours.png
   :scale: 50




As can already be observed in the examples with :class:`GeomSmooth`,
several *geometry* objects can be added on the top of eachother
in order to create the final plot. For example, a marginal *rug*
can be added to the axis of a regular scatterplot:

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2geompointandrug-begin
   :end-before: #-- ggplot2geompointandrug-end
   
.. image:: _static/graphics_ggplot2geompointandrug.png
   :scale: 50






Facets
^^^^^^

Splitting the data into panels, in a similar fashion to what we did
with *lattice*, is now a matter of adding *facets*. 
A central concept to *ggplot2* is that plot are made of added
graphical elements, and adding specifications such as "I want my data
to be split in panel" is then a matter of adding that information
to an existing plot.

For example, splitting the plots on the data in column *cyl* 
is still simply done by adding a :class:`FacetGrid`.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2smoothbycylfacetcyl-begin
   :end-before: #-- ggplot2smoothbycylfacetcyl-end

   
.. image:: _static/graphics_ggplot2smoothbycylfacetcyl.png
   :scale: 50


The way data are represented (the *geometry* in the terminology
used the grammar of graphics) are still specified the usual way.

.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2histogramfacetcyl-begin
   :end-before: #-- ggplot2histogramfacetcyl-end

   
.. image:: _static/graphics_ggplot2histogramfacetcyl.png
   :scale: 50






.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- qplot4-begin
   :end-before: #-- qplot4-end
   
.. image:: _static/graphics_ggplot2_qplot_4.png
   :scale: 50


.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- qplot3addline-begin
   :end-before: #-- qplot3addline-end

   
.. image:: _static/graphics_ggplot2_qplot_5.png
   :scale: 50



.. literalinclude:: _static/demos/graphics.py
   :start-after: #-- ggplot2smoothblue-begin
   :end-before: #-- ggplot2smoothblue-end

   
.. image:: _static/graphics_ggplot2smoothblue.png
   :scale: 50







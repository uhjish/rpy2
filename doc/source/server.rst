.. _misc-server:

*************
Client-Server
*************

Rserve is currently the default solution when looking
for a server solution for R, but :mod:`rpy2` can be used
to develop very easily one's own server, tailored to answer
specific requirements. Such requirements can include for example
access restriction, a security model, access to subsets of the R
engine, distribution of jobs to other servers, all of which
are currently difficult or impossible to achieve with R serve.


The :mod:`pyRserve` package addresses the connection to Rserve
from Python, and is therefore limited to Rserve servers only.


Simple socket-based server and client
=====================================

Server
------

An implementation of a simplistic socket server listening
on a given port

.. literalinclude:: _static/demos/rpyserve.py


Running a server listening on port 9090 is then:

.. code-block:: bash

   python rpyserve.py 9090


Client
------

.. literalinclude:: _static/demos/rpyclient.py


Evaluating R code on a local server defined as above, listening on
port 9090 is then:

.. code-block:: bash

   python rpyclient.py localhost:9090 'R.version'

In this example, the client is querying the R version.



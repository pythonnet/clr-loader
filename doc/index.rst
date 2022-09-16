.. clr-loader documentation master file, created by
   sphinx-quickstart on Fri Sep 16 17:57:02 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to clr-loader's documentation!
======================================

`clr_loader` provides a unified way to load one of the CLR (.NET) runtime
implementations (.NET Framework, .NET (Core) or Mono), load assemblies, and call
very simple functions.

The only supported signature is

.. code-block:: csharp

   public static int Function(IntPtr buffer, int size)

A function like this can be called from Python with a single ``bytes``
parameter. If more functionality is required, please consider using `Python.NET
<https://pythonnet.github.io>`_ instead.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

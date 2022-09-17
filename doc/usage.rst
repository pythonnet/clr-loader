Usage
=====

.. py:currentmodule:: clr_loader

Getting a runtime
-----------------

To get a :py:class:`Runtime` instance, one of the ``get_*`` functions has to be
called. There are currently the factory functions :py:func:`get_mono`,
:py:func:`get_coreclr` and :py:func:`get_netfx`. All of these provide various
configuration options that are documented in the :ref:`Reference <reference>`.
They also provide reasonable defaults and can be called without parameters if
the respective runtime is installed globally:

.. code-block:: python

    from clr_loader import get_coreclr
    runtime = get_coreclr()

After this, the runtime will usually already be initialized. The initialization
is delayed for .NET Core to allow adjusting the runtime properties beforehand.

Information on the runtime, its version and parameters can be retrieved using
``runtime.info()`` (see :py:func:`Runtime.info`).

Getting a callable function
---------------------------

A wrapped assembly can be retrieved from the runtime by calling
:py:func:`Runtime.get_assembly` with the path.

The following example class is provided in the repository:

.. code-block:: csharp

    using System.Text;
    using System.Runtime.InteropServices;
    using System;

    namespace Example
    {
        public class TestClass
        {
            public static int Test(IntPtr arg, int size) {
                var buf = new byte[size];
                Marshal.Copy(arg, buf, 0, size);
                var bufAsString = Encoding.UTF8.GetString(buf);
                var result = bufAsString.Length;
                Console.WriteLine($"Called {nameof(Test)} in {nameof(TestClass)} with {bufAsString}, returning {result}");
                Console.WriteLine($"Binary data: {Convert.ToBase64String(buf)}");

                return result;
            }
        }
    }

Assuming it has been compiled to ``out/example.dll``, it can now be loaded using
:py:func:`Runtime.get_assembly`:

.. code-block:: python

   assembly = runtime.get_assembly("path/to/assembly.dll")

.. note::
   This does *not* guarantee that the DLL is already loaded and will not
   necessarily trigger an error if that is not possible. Actually resolving the
   DLL only happens (for all implementations but Mono) when retrieving the
   concrete function.

The ``assembly`` instance can now be used to get a wrapper instance of the
``Test`` function in Python. The given parameters are the fully qualified class
name and the function name. Alternatively, a single parameter can be provided,
and we assume that the last "component" is the function name. These are
equivalent:

.. code-block:: python

   function = assembly.get_function("Example.TestClass", "Test")
   function = assembly.get_function("Example.TestClass.Test")

This function can now be called with a Python ``binary`` like this:

.. code-block:: python

   result = function(b"testy mctestface")

The ``IntPtr`` parameter in C# will now point directly at the ``binary`` buffer,
the ``int`` parameter will contain the size. The given call will thus result in
the output:

.. code-block:: output

   Called Test in TestClass with testy mctestface, returning 16
   Binary data: dGVzdHkgbWN0ZXN0ZmFjZQ==

``result`` will now be ``16``.

.. warning::
   While the buffer can theoretically also be changed in the .NET function, this
   is not tested.

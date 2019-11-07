using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using NXPorts.Attributes;

namespace ClrLoader
{
    using DllExportAttribute = ExportAttribute;
    
    public static class ClrLoader
    {
        delegate int EntryPoint(IntPtr buffer, int size);

        [DllExport("pyclr_create_appdomain", CallingConvention.Cdecl)]
        public static IntPtr CreateAppDomain(
            [MarshalAs(UnmanagedType.LPUTF8Str)] string name,
            [MarshalAs(UnmanagedType.LPUTF8Str)] string configFile
        )
        {
            Print($"Creating AppDomain {name} with {configFile}");
            if (!string.IsNullOrEmpty(name))
            {
                var setup = new AppDomainSetup
                {
                    ConfigurationFile = configFile
                };
                var domain = AppDomain.CreateDomain(name, null, setup);

                Print($"Located domain {domain}");

                var handle = GCHandle.Alloc(domain, GCHandleType.Pinned);

                Print($"Created handle {handle}");

                return handle.AddrOfPinnedObject();
            }
            else
            {
                return IntPtr.Zero;
            }
        }

        [DllExport("pyclr_get_function", CallingConvention.Cdecl)]
        public static IntPtr GetFunction(
            IntPtr domain,
            [MarshalAs(UnmanagedType.LPStr)] string assemblyPath,
            [MarshalAs(UnmanagedType.LPStr)] string typeName,
            [MarshalAs(UnmanagedType.LPStr)] string function
        )
        {
            try
            {
                var domainObj = AppDomain.CurrentDomain;
                if (domain != IntPtr.Zero)
                {
                    var handle = GCHandle.FromIntPtr(domain);
                    domainObj = (AppDomain)handle.Target;
                }

                var assembly = domainObj.Load(AssemblyName.GetAssemblyName(assemblyPath));
                var type = assembly.GetType(typeName, throwOnError: true);
                Print($"Loaded type {type}");
                var deleg = Delegate.CreateDelegate(typeof(EntryPoint), type, function);

                return Marshal.GetFunctionPointerForDelegate(deleg);
            }
            catch (Exception exc)
            {
                Print($"Exception in {nameof(GetFunction)}: {exc.GetType().Name} {exc.Message}\n{exc.StackTrace}");
                return IntPtr.Zero;
            }
        }

        [DllExport("pyclr_close_appdomain", CallingConvention.Cdecl)]
        public static void CloseAppDomain(IntPtr domain)
        {
            if (domain != IntPtr.Zero)
            {
                var handle = GCHandle.FromIntPtr(domain);
                var domainObj = (AppDomain)handle.Target;
                AppDomain.Unload(domainObj);
                handle.Free();
            }
        }

        static void Print(string s)
        {
            Console.WriteLine(s);
        }
    }

}

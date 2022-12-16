using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using NXPorts.Attributes;

namespace ClrLoader
{
    public static class ClrLoader
    {
        static bool _initialized = false;
        static List<DomainData> _domains = new List<DomainData>();

        [DllExport("pyclr_initialize", CallingConvention.Cdecl)]
        public static void Initialize()
        {
            if (!_initialized)
            {
                _domains.Add(new DomainData(AppDomain.CurrentDomain));
                _initialized = true;
            }
        }

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
                    ApplicationBase = AppDomain.CurrentDomain.BaseDirectory,
                    ConfigurationFile = configFile
                };
                Print($"Base: {AppDomain.CurrentDomain.BaseDirectory}");
                var domain = AppDomain.CreateDomain(name, null, setup);

                Print($"Located domain {domain}");

                var domainData = new DomainData(domain);
                _domains.Add(domainData);
                return new IntPtr(_domains.Count - 1);
            }
            else
            {
                return IntPtr.Zero;
            }
        }

        [DllExport("pyclr_get_function", CallingConvention.Cdecl)]
        public static IntPtr GetFunction(
            IntPtr domain,
            [MarshalAs(UnmanagedType.LPUTF8Str)] string assemblyPath,
            [MarshalAs(UnmanagedType.LPUTF8Str)] string typeName,
            [MarshalAs(UnmanagedType.LPUTF8Str)] string function
        )
        {
            try
            {
                var domainData = _domains[(int)domain];
                var deleg = domainData.GetEntryPoint(assemblyPath, typeName, function);
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
                try
                {
                    var domainData = _domains[(int)domain];
                    domainData.Dispose();
                }
                catch (Exception exc)
                {
                    Print($"Exception in {nameof(CloseAppDomain)}: {exc.GetType().Name} {exc.Message}\n{exc.StackTrace}");
                }
            }
        }

        [DllExport("pyclr_finalize", CallingConvention.Cdecl)]
        public static void Close()
        {
            foreach (var domainData in _domains)
            {
                domainData.Dispose();
            }

            _domains.Clear();
            _initialized = false;
        }

#if DEBUG
        internal static void Print(string s)
        {
            Console.WriteLine(s);
        }
#else
        internal static void Print(string s) { }
#endif
    }

}

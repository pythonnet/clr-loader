using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.InteropServices;

namespace ClrLoader
{
    using static ClrLoader;

    public static class DomainSetup
    {
        public delegate int EntryPoint(IntPtr buffer, int size);

        public static void StoreFunctorFromDomainData()
        {
            var domain = AppDomain.CurrentDomain;
            var assemblyPath = (string)domain.GetData("_assemblyPath");
            var typeName = (string)domain.GetData("_typeName");
            var function = (string)domain.GetData("_function");
            var deleg = GetDelegate(domain, assemblyPath, typeName, function);
            var functor = Marshal.GetFunctionPointerForDelegate(deleg);
            domain.SetData("_thisDelegate", deleg);
            domain.SetData("_thisFunctor", functor);
        }

        private static Delegate GetDelegate(AppDomain domain, string assemblyPath, string typeName, string function)
        {
            var assemblyName = AssemblyName.GetAssemblyName(assemblyPath);
            var assembly = domain.Load(assemblyName);
            var type = assembly.GetType(typeName, throwOnError: true);
            var deleg = Delegate.CreateDelegate(typeof(EntryPoint), type, function);
            return deleg;
        }
    }

    class DomainData : IDisposable
    {
        bool _disposed = false;

        public AppDomain Domain { get; }
        public Dictionary<(string, string, string), IntPtr> _functors;
        public HashSet<string> _resolvedAssemblies;

        public DomainData(AppDomain domain)
        {
            Domain = domain;
            _functors = new Dictionary<(string, string, string), IntPtr>();
            _resolvedAssemblies = new HashSet<string>();
        }

        private void installResolver(string assemblyPath)
        {
            var assemblyName = AssemblyName.GetAssemblyName(assemblyPath).Name;
            if (_resolvedAssemblies.Contains(assemblyName))
                return;
            _resolvedAssemblies.Add(assemblyName);

            AppDomain.CurrentDomain.AssemblyResolve += (sender, args) =>
            {
                if (args.Name.Contains(assemblyName))
                    return Assembly.LoadFrom(assemblyPath);
                return null;
            };
        }

        private static readonly object _lockObj = new object();

        public IntPtr GetFunctor(string assemblyPath, string typeName, string function)
        {
            if (_disposed)
                throw new InvalidOperationException("Domain is already disposed");

            // neither the domain data nor the _functors dictionary is threadsafe
            lock (_lockObj)
            {
                installResolver(assemblyPath);
                var assemblyName = AssemblyName.GetAssemblyName(assemblyPath).Name;

                var key = (assemblyName, typeName, function);

                IntPtr result;
                if (!_functors.TryGetValue(key, out result))
                {
                    Domain.SetData("_assemblyPath", assemblyPath);
                    Domain.SetData("_typeName", typeName);
                    Domain.SetData("_function", function);

                    Domain.DoCallBack(new CrossAppDomainDelegate(DomainSetup.StoreFunctorFromDomainData));
                    result = (IntPtr)Domain.GetData("_thisFunctor");
                    if (result == IntPtr.Zero)
                        throw new Exception($"Unable to get functor for {assemblyName}, {typeName}, {function}");

                    // set inputs to StoreFunctorFromDomainData to null.
                    // (There's no method to explicitly clear domain data)
                    Domain.SetData("_assemblyPath", null);
                    Domain.SetData("_typeName", null);
                    Domain.SetData("_function", null);

                    // the result has to remain in the domain data because we don't know when the
                    // client of pyclr_get_function will actually invoke the functor, and if we
                    // remove it from the domain data after returning it may get collected too early.
                    _functors[key] = result;
                }
                return result;
            }
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                _functors.Clear();

                if (Domain != AppDomain.CurrentDomain)
                    AppDomain.Unload(Domain);

                _disposed = true;
            }
        }

    }
}
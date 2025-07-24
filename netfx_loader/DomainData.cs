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
            var functor = GetFunctor(domain, assemblyPath, typeName, function);
            domain.SetData("_thisFunctor", functor);
        }

        private static IntPtr GetFunctor(AppDomain domain, string assemblyPath, string typeName, string function)
        {
            var assemblyName = AssemblyName.GetAssemblyName(assemblyPath).Name;
            var assembly = domain.Load(AssemblyName.GetAssemblyName(assemblyPath));
            var type = assembly.GetType(typeName, throwOnError: true);
            var deleg = Delegate.CreateDelegate(typeof(EntryPoint), type, function);
            IntPtr result = Marshal.GetFunctionPointerForDelegate(deleg);
            return result;
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

        public IntPtr GetFunctor(string assemblyPath, string typeName, string function)
        {
            if (_disposed)
                throw new InvalidOperationException("Domain is already disposed");

            installResolver(assemblyPath);

            var key = (assemblyPath, typeName, function);

            IntPtr result;
            if (!_functors.TryGetValue(key, out result))
            {
                Domain.SetData("_assemblyPath", assemblyPath);
                Domain.SetData("_typeName", typeName);
                Domain.SetData("_function", function);

                Domain.DoCallBack(new CrossAppDomainDelegate(DomainSetup.StoreFunctorFromDomainData));
                result = (IntPtr)Domain.GetData("_thisFunctor");
                _functors[key] = result;
            }
            return result;
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
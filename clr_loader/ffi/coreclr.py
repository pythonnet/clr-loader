cdef = [
    """
__stdcall unsigned int coreclr_initialize(
    const char* exePath,
    const char* appDomainFriendlyName,
    int propertyCount,
    const char** propertyKeys,
    const char** propertyValues,
    void** hostHandle,
    unsigned* domainId
);

__stdcall unsigned int coreclr_execute_assembly(
    void* hostHandle,
    unsigned int domainId,
    int argc,
    const char** argv,
    const char* managedAssemblyPath,
    unsigned int* exitCode
);

__stdcall unsigned int coreclr_create_delegate(
    void* hostHandle,
    unsigned int domainId,
    const char* entryPointAssemblyName,
    const char* entryPointTypeName,
    const char* entryPointMethodName,
    void** delegate
);

__stdcall int coreclr_shutdown(void* hostHandle, unsigned int domainId);
"""
]

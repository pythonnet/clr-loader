#!/usr/bin/env python

from setuptools import setup, find_packages, Command, Extension
from wheel.bdist_wheel import bdist_wheel


class DotnetLib(Extension):
    def __init__(self, name, path, **kwargs):
        self.path = path
        self.args = kwargs
        super().__init__(name, sources=[])


class BuildDotnet(Command):
    """Build command for dotnet-cli based builds"""

    description = "Build DLLs with dotnet-cli"
    user_options = [("dotnet-config", None, "dotnet build configuration")]

    def initialize_options(self):
        self.dotnet_config = "release"

    def finalize_options(self):
        pass

    def get_source_files(self):
        return []

    def run(self):
        for lib in self.distribution.ext_modules:
            opts = sum(
                [
                    ["--" + name.replace("_", "-"), value]
                    for name, value in lib.args.items()
                ],
                [],
            )

            opts.append("--configuration")
            opts.append(self.dotnet_config)

            self.spawn(["dotnet", "build", lib.path] + opts)


class bdist_wheel_patched(bdist_wheel):
    def finalize_options(self):
        # Monkey patch bdist_wheel to think the package is pure even though we
        # include DLLs
        super().finalize_options()
        self.root_is_pure = True


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="clr_loader",
    version="0.1.0",
    description="Generic pure Python loader for .NET runtimes",
    author="Benedikt Reinartz",
    author_email="filmor@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.3",
    install_requires=["cffi>=1.13"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    package_data={"clr_loader.ffi": ["dlls/x86/*.dll", "dlls/amd64/*.dll"]},
    packages=find_packages(),
    cmdclass={"build_ext": BuildDotnet, "bdist_wheel": bdist_wheel_patched},
    ext_modules={
        DotnetLib(
            "netfx-loader-x86",
            "netfx_loader/ClrLoader.csproj",
            runtime="win-x86",
            output="clr_loader/ffi/dlls/x86",
        ),
        DotnetLib(
            "netfx-loader-amd64",
            "netfx_loader/ClrLoader.csproj",
            runtime="win-x64",
            output="clr_loader/ffi/dlls/amd64",
        ),
    },
)

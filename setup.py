#!/usr/bin/env python

from distutils.core import setup

setup(
    name="clr_loader",
    version="0.1.0",
    description="Generic pure Python loader for .NET runtimes",
    author="Benedikt Reinartz",
    author_email="filmor@gmail.com",
    license="MIT",
    install_requires=["cffi"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    package_data={"clr_loader.ffi": ["dlls/x86/*", "dlls/amd64/*"]},
    packages=["clr_loader", "clr_loader.ffi", "clr_loader.util"],
)

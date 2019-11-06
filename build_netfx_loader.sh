#!/bin/sh

S=`dirname $0`
P=netfx_loader/
O=clr_loader/ffi/dlls/

dotnet build $P -r win-x86 -o $O/x86
dotnet build $P -r win-x64 -o $O/amd64

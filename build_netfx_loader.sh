#!/bin/sh

S=`dirname $0`
P=netfx_loader/
O=$S/clr_loader/ffi/dlls/

mkdir -p "$O" || exit -1

dotnet build "$P" -r win-x86 -o "$O/x86" || exit -1
dotnet build "$P" -r win-x64 -o "$O/amd64" || exit -1

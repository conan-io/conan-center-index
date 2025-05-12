# mold: A Modern Linker

mold is a faster drop-in replacement for existing Unix linkers. It is several
times quicker than the LLVM lld linker, the second-fastest open-source linker.
mold aims to enhance developer productivity by minimizing build time, 
particularly in rapid debug-edit-rebuild cycles.

You can configure Conan to download the latest version of `mold` and use it as the linker 
when building your dependencies and projects from source. Currently only supported
when targeting Linux as the platform.

To use mold automatically as the linker, you can add the following section to your
_host_ profile that targets Linux. When using gcc, please note that the following
flags require gcc 12.1 or greater.

```
[tool_requires]
*:mold/[*]
[conf]
tools.build:exelinkflags=['-fuse-ld=mold']
tools.build:sharedlinkflags=['-fuse-ld=mold']
```

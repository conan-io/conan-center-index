# mold: A Modern Linker

mold is a faster drop-in replacement for existing Unix linkers. It is several
times quicker than the LLVM lld linker, the second-fastest open-source linker.
mold aims to enhance developer productivity by minimizing build time, 
particularly in rapid debug-edit-rebuild cycles.

You can configure [Conan](https://github.com/conan-io) to download the latest
version of `mold` and use it as the linker when building your dependencies and
projects from source.

Add the following section to your _host_ profile targeting Linux:

```
[tool_requires]
*:mold/[*]
[conf]
# The following config will only work with clang or gcc >= 12
tools.build:exelinkflags=['-fuse-ld=mold']
tools.build:sharedlinkflags=['-fuse-ld=mold']
```

# Supported platforms and configurations


- For a **C++** library (with ``"shared"`` option) the system is generating **136** binary packages.
- For a **pure C** library (with ``"shared"`` option but without ``compiler.libcxx``) the system generates **88** binary packages.
- A package is also generated for those recipes with the `"header_only"` option.

## Windows

- Compilers: Visual Studio:
  - 2015 (14.0.25431.01 Update 3)
  - 2017 (15.9.19+28307.1000)
  - 2019 (16.4.4+29728.190)
- Release (MT/MD) and Debug (MTd, MDd)
- Architectures: x86_64
- Build types: Release, Debug
- Runtimes: MT/MD (Release), MTd/MDd (Debug)
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

## Linux

- Compilers:
  - GCC versions 4.9, 5, 6, 7, 8, 9
  - Clang versions 3.9, 4.0, 5.0, 6.0, 7.0, 8, 9
- C++ Standard Library (`libcxx`):
  - GCC compiler: `libstdc++`, `libstdc++11`
  - Clang compiler: `libstdc++`, `libc++`
- Architectures: x86_64
- Build types: Release, Debug
- Options:
  - Shared, Static (option `"shared": [True, False]` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

## OSX

- Compilers: Apple-clang versions 9.1, 10.0, 11.0 (three latest versions, we will rotate the older when a new compiler version is released)
- C++ Standard Library (`libcxx`): `libc++`
- Architectures: x86_64
- Build types: Release, Debug
- Options:
  - Shared, Static (option ``"shared": [True, False]`` in the recipe when available)
  - Header Only (option `"header_only": [True, False]` is only added with the value True)

# `src/samarium`

This directory contains all the relevant source code of the library.

It is broken up into modules, each with its own subdirectory.

- `core` : the core parts of `samarium`: versioning, typedefs, arrays, threading

- `math`: all the math needed for computations:
  - `math` for math functions
  - `Vector2` for 2d vectors
  - `geometry` for vector math
  - `shapes` for basic wrappers around shapes
  - `Extents`, `interp` and `BoundingBox` for bounds and interpolation

- `util` for printing, formatting and file output

- `graphics` for colors, images and rendering

- `gui` for window management and the user interface

- `physics` for simulation

> For installation and more, see [the README on Github](https://github.com/strangeQuark1041/samarium#prerequistes)

# Components

## Core

### types

For uniformity with using primitives, typedefs are used, for e.g. `i32` for `int` and `f64` for `double`

### concepts

[C++20's concepts](https://en.cppreference.com/w/cpp/language/constraints) are used to both constrain templates, and overload functions based on types

Docs: <https://strangequark1041.github.io/samarium/concepts_8hpp.html>

### ThreadPool

A dedicated thread pool object should be in lieu of `std::thread`' s which are expensive to create.
ThreadPool also has the convenient `parallelize_loop` function, which can massively speed up raw for loops

Main page: <https://github.com/bshoshany/thread-pool>

Docs: <https://strangequark1041.github.io/samarium/classsm_1_1ThreadPool.html>

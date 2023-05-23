#include "benchmark/cppbenchmark.h"

#include <cmath>

// Benchmark sin() call for 1 seconds.
// Make 1 attemtps and choose one with the best time result.
BENCHMARK("sin", Settings().Duration(1).Operations(1).Attempts(1))
{
    std::sin(123.456);
}

BENCHMARK_MAIN()

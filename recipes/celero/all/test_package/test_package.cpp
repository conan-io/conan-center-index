#include <celero/Celero.h>

#include <cmath>
#include <random>

///
/// This is the main(int argc, char** argv) for the entire celero program.
/// You can write your own, or use this macro to insert the standard one into the project.
///
CELERO_MAIN

std::random_device RandomDevice;
std::uniform_int_distribution<int> UniformDistribution(0, 1024);

///
/// In reality, all of the "Complex" cases take the same amount of time to run.
/// The difference in the results is a product of measurement error.
///
/// Interestingly, taking the sin of a constant number here resulted in a
/// great deal of optimization in clang and gcc.
///
BASELINE(DemoSimple, Baseline, 10, 100000)
{
    celero::DoNotOptimizeAway(static_cast<float>(std::sin(UniformDistribution(RandomDevice))));
}

///
/// Run a test consisting of 1 sample of 710000 operations per measurement.
/// There are not enough samples here to likely get a meaningful result.
///
BENCHMARK(DemoSimple, Complex1, 1, 710000)
{
    celero::DoNotOptimizeAway(static_cast<float>(std::sin(std::fmod(UniformDistribution(RandomDevice), 3.14159265))));
}

#include <cstdlib>
#include <amgcl/profiler.hpp>

int main() {
    amgcl::profiler<> profile;
    profile.tic("assemble");

    return EXIT_SUCCESS;
}

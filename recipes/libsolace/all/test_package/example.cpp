#include "solace/version.hpp"

int main() {
    return Solace::getBuildVersion().build.empty()
            ? 0
            : 1;
}

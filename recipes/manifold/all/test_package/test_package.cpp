#include <cstdlib>
#include "manifold/manifold.h"
#include "manifold/polygon.h"

using namespace manifold;

int main(void) {
    ManifoldParams().intermediateChecks = true;
    ManifoldParams().processOverlaps = false;
    ManifoldParams().suppressErrors = true;

    Polygons polys;
    polys.emplace_back();
    polys.back().emplace_back(1, 1);

    return EXIT_SUCCESS;
}

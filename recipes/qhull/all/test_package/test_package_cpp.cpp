#include <iostream>
#include "libqhullcpp/Qhull.h"
#include "libqhullcpp/QhullFacetList.h"
#include "libqhullcpp/QhullVertexSet.h"

using namespace orgQhull;

int main() {
    // Example: 6 points in 3D forming a cube corner
    double points[] = {
        0.0, 0.0, 0.0,
        1.0, 0.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, 0.0, 1.0,
        1.0, 1.0, 0.0,
        0.0, 1.0, 1.0
    };
    int numPoints = sizeof(points) / (3 * sizeof(double));
    int dim = 3;

    try {
        // Run Qhull with "convex hull" option (Qt: triangulated hull, s: summary output)
        Qhull qhull;
        qhull.runQhull("example", dim, numPoints, points, "Qt s");

        std::cout << "Convex hull computed with " << qhull.facetCount() << " facets" << std::endl;

        // Iterate facets and their vertices
        for(const QhullFacet &facet : qhull.facetList()){
            if(!facet.isGood()) continue; // skip upper Delaunay facets
            std::cout << "Facet:";
            for(const QhullVertex &v : facet.vertices()){
                const double *coords = v.point().coordinates();
                std::cout << " ("
                          << coords[0] << ", "
                          << coords[1] << ", "
                          << coords[2] << ")";
            }
            std::cout << std::endl;
        }

    } catch (std::exception &e) {
        std::cerr << "Qhull error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

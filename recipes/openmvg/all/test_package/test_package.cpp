#include <openMVG/geometry/convex_hull.hpp>
#include <openMVG/linearProgramming/linearProgramming.hpp>
#include <openMVG/multiview/conditioning.hpp>
#include <openMVG/numeric/numeric.h>

int main() {
    // Test symbols of openMVG_geometry
    openMVG::geometry::Polygon2d polygon;
    polygon.emplace_back(0.0, 0.0);
    polygon.emplace_back(0.0, 2.0);
    polygon.emplace_back(1.0, 2.0);
    polygon.emplace_back(5.0, 1.2);
    polygon.emplace_back(0.0, 0.0);
    double area;
    auto ret = openMVG::geometry::ConvexPolygonArea(polygon, area);

    // Test symbols of openMVG_linearProgramming
    openMVG::linearProgramming::OSI_CLP_SolverWrapper solver(10);

    // Test symbols of openMVG_multiview
    openMVG::Mat3 mat;
    openMVG::PreconditionerFromPoints(1024, 1024, &mat);
    return 0;
}

#include <omath/omath.hpp>
#include <iostream>

int main()
{
    omath::pathfinding::NavigationMesh nav;
    constexpr omath::Vector3<float> v{1.f, 1.f, 0.f};
    nav.m_vertex_map[v] = {};
    const auto path = omath::pathfinding::Astar::find_path(v, v, nav);
    std::cout << "Omath Path size: " << path.size() << std::endl;
    return 0;
}

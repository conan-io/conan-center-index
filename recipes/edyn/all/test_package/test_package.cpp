#include <edyn/edyn.hpp>
#include <cassert>

int main()
{
    edyn::vector3 const v0{ 0, 1, 2 };
    edyn::vector3 const v1{ -2, -1, -0 };

    std::printf("%f\n", edyn::dot(v0, v1));
    assert(edyn::dot(v0, v1) == -1);
}

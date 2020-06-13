#include <pcl/point_types.h>

#include <iostream>

int main() {
    pcl::PointXYZ p;
    p.x = -1.0f;
    p.y = 3.14f;
    p.z = 42.0f;

    std::cout << "PointXYZ: " << p << std::endl;
}

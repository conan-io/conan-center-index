#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/surface/convex_hull.h>

#include <iostream>

int main() {

    auto cloud = std::make_shared<pcl::PointCloud<pcl::PointXYZ>>();
    cloud->emplace_back(-1, -1, 0);
    cloud->emplace_back(1, -1, 0);
    cloud->emplace_back(0, 1, 0);
    cloud->emplace_back(0, 0, 1);

    std::cout << "Calculating convex hull\n";

    pcl::PointCloud<pcl::PointXYZ> hull_geometry;

    pcl::ConvexHull<pcl::PointXYZ> hull;
    hull.setInputCloud(cloud);
    hull.setComputeAreaVolume(true);
    hull.reconstruct(hull_geometry);

    std::cout << "Convex Hull Volume: " << hull.getTotalVolume() << std::endl;
}

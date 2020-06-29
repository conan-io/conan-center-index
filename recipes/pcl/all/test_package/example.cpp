#include <pcl/point_types.h>
#include <pcl/point_cloud.h>
#include <pcl/surface/convex_hull.h>

#include <iostream>
    
using PointCloud = pcl::PointCloud<pcl::PointXYZ>;

int main() {

    auto cloud = PointCloud::Ptr(new PointCloud);
    cloud->emplace_back(-1, -1, 0);
    cloud->emplace_back(1, -1, 0);
    cloud->emplace_back(0, 1, 0);
    cloud->emplace_back(0, 0, 1);

    std::cout << "Calculating convex hull\n";

    PointCloud hull_geometry;

    pcl::ConvexHull<pcl::PointXYZ> hull;
    hull.setInputCloud(cloud);
    hull.setComputeAreaVolume(true);
    hull.reconstruct(hull_geometry);

    std::cout << "Convex Hull Volume: " << hull.getTotalVolume() << std::endl;
}

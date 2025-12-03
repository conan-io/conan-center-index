// TO BE REMOVED BEFORE MERGE
#include <iostream>
#include <pcl/point_types.h>
#include <pcl/features/normal_3d_omp.h>

int main()
{
    // Create fake input cloud
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new pcl::PointCloud<pcl::PointXYZ>());
    cloud->resize(1000);
    for (std::size_t i = 0; i < cloud->size(); i++) {
        (*cloud)[i].x = float(i);
        (*cloud)[i].y = float(i) * 0.1f;
        (*cloud)[i].z = float(i) * 0.01f;
    }

    pcl::NormalEstimationOMP<pcl::PointXYZ, pcl::Normal> ne;
    
    // Try using 4 threads
    ne.setNumberOfThreads(4);
    std::cout << "Requested threads = 4\n";

    ne.setInputCloud(cloud);
    ne.setRadiusSearch(0.1);

    pcl::PointCloud<pcl::Normal> normals;
    ne.compute(normals);

    std::cout << "Computed normals: " << normals.size() << "\n";

    return 0;
}

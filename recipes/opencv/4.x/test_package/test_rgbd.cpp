#include <opencv2/core.hpp>
#include <opencv2/rgbd/depth.hpp>

int main() {
    auto depth_cleaner = cv::rgbd::DepthCleaner::create(5);
    return 0;
}

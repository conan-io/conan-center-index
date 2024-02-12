#include <opencv2/hfs.hpp>

int main() {
    auto hfs_segment = cv::hfs::HfsSegment::create(100, 100);
    return 0;
}

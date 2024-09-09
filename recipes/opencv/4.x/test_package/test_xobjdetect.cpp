#include <opencv2/xobjdetect.hpp>

int main() {
    auto detector = cv::xobjdetect::WBDetector::create();
    return 0;
}

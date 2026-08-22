#include <opencv2/features2d.hpp>

int main() {
    auto matcher = cv::DescriptorMatcher::create(cv::DescriptorMatcher::BRUTEFORCE);
    return 0;
}

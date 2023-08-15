#include <opencv2/core.hpp>
#include <opencv2/sfm.hpp>

int main() {
    cv::Vec3f a;
    a << 1,2,3;
    cv::Matx33f ax = cv::sfm::skew(a);

    return 0;
}

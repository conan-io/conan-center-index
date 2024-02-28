#include <opencv2/core.hpp>
#include <opencv2/photo.hpp>

int main() {
    auto src_image = cv::Mat::zeros(400, 400, CV_8UC3);
    cv::Mat dst_image;
    cv::fastNlMeansDenoising(src_image, dst_image);

    return 0;
}

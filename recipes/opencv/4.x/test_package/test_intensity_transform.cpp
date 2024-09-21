#include <opencv2/core.hpp>
#include <opencv2/intensity_transform.hpp>

int main() {
    cv::Mat src_image = cv::Mat::zeros(400, 400, CV_8UC3);
    cv::Mat dst_image;
    cv::intensity_transform::autoscaling(src_image, dst_image);
    return 0;
}

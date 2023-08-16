#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>

int main() {
    cv::Mat img = cv::Mat::zeros(400, 400, CV_8UC3);
    cv::imwrite("test_imgcodecs.png", img);

    return 0;
}

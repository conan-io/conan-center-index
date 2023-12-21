#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

int main() {
    const int width = 400;
    cv::Mat image = cv::Mat::zeros(width, width, CV_8UC3);

    cv::ellipse(
        image, cv::Point(width / 2, width / 2), cv::Size(width / 4, width / 16),
        90, 0, 360, cv::Scalar(255, 0, 0), 2, 8
    );

    return 0;
}

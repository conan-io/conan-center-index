#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>

int main() {
    cv::Mat image = cv::Mat::zeros(400, 400, CV_8UC3);
    cv::imshow("test highgui", image);
    return 0;
}

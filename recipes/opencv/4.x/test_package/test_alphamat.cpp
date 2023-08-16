#include <opencv2/core.hpp>
#include <opencv2/alphamat.hpp>

int main() {
    cv::Mat image = cv::Mat::ones(400, 400, CV_8UC3) * 50;
    cv::Mat tmap = cv::Mat::ones(400, 400, CV_8U) * 120;
    cv::Mat result;
    cv::alphamat::infoFlow(image, tmap, result);
    return 0;
}

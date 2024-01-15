#include <opencv2/core.hpp>
#include <opencv2/text/erfilter.hpp>

#include <vector>

int main() {
    cv::Mat image = cv::Mat::zeros(10, 10, CV_8UC3);
    std::vector<cv::Mat> channels;
    cv::text::computeNMChannels(image, channels);
    return 0;
}

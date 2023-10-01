#include <opencv2/core.hpp>
#include <opencv2/img_hash/average_hash.hpp>

int main() {
    cv::Mat image = cv::Mat::zeros(400, 400, CV_8UC3);
    auto func = cv::img_hash::AverageHash::create();
    cv::Mat hash;
    func->compute(image, hash);
    return 0;
}

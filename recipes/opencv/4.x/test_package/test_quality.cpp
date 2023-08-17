#include <opencv2/core.hpp>
#include <opencv2/quality/qualitymse.hpp>

int main() {
    cv::Mat image = cv::Mat::ones(10, 10, CV_8UC3) * 40;
    auto quality_mse = cv::quality::QualityMSE::create(image);
    return 0;
}

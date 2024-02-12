#include <opencv2/core.hpp>
#include <opencv2/plot.hpp>

int main() {
    cv::Mat xData;
    xData.create(1, 100, CV_64F);
    for (int i = 0; i < 100; ++i) {
        xData.at<double>(i) = i / 10.0;
    }
    auto plot = cv::plot::Plot2d::create(xData);
    return 0;
}

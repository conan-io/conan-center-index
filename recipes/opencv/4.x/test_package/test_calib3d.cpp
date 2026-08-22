#include <opencv2/calib3d.hpp>
#include <opencv2/core.hpp>

#include <cmath>
#include <vector>

int main() {
    const int point_count = 100;
    std::vector<cv::Point2f> points1;
    points1.reserve(point_count);
    std::vector<cv::Point2f> points2;
    points2.reserve(point_count);
    for (int i = 0; i < point_count; ++i) {
        points1.emplace_back(
            cv::Point2f(static_cast<float>(100 + 30 * std::cos(i * CV_PI * 2 / 5)),
                        static_cast<float>(100 - 30 * std::sin(i * CV_PI * 2 / 5)))
        );
        points2.emplace_back(
            cv::Point2f(static_cast<float>(100 + 30 * std::sin(i * CV_PI * 2 / 5)),
                        static_cast<float>(100 - 30 * std::cos(i * CV_PI * 2 / 5)))
        );
    }
    auto fundamental_matrix = cv::findFundamentalMat(points1, points2, cv::FM_RANSAC, 3, 0.99);

    return 0;
}

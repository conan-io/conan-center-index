#include <opencv2/core.hpp>
#include <opencv2/flann.hpp>

#include <cmath>
#include <vector>

int main() {
    const int point_count = 100;
    std::vector<cv::Point2f> points;
    points.reserve(point_count);
    for (int i = 0; i < point_count; ++i) {
        points.emplace_back(
            cv::Point2f(static_cast<float>(100 + 30 * std::cos(i * CV_PI * 2 / 5)),
                        static_cast<float>(100 - 30 * std::sin(i * CV_PI * 2 / 5)))
        );
    }

    cv::flann::KDTreeIndexParams indexParams;
    cv::flann::Index kdtree(cv::Mat(points).reshape(1), indexParams);

    std::vector<float> query{110, 98};

    std::vector<int> indices;
    std::vector<float> dists;
    kdtree.knnSearch(query, indices, dists, 3);

    return 0;
}

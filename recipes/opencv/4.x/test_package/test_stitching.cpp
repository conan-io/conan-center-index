#include <opencv2/core.hpp>
#include <opencv2/stitching/detail/util.hpp>

int main() {
    cv::Rect roi;
    bool overlap = cv::detail::overlapRoi(
        cv::Point2f(2, 3), cv::Point2f(4, -3),
        cv::Size(10, 10), cv::Size(3, 4),
        roi
    );

    return 0;
}

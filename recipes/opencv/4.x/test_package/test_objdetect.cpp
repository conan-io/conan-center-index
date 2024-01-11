#include <opencv2/core.hpp>
#include <opencv2/objdetect.hpp>

#include <vector>

int main() {
    std::vector<cv::Rect> rectangles;
    rectangles.reserve(100);
    for (int i = 0; i < 10; ++i) {
        for (int j = 0; j < 10; ++j) {
            rectangles.emplace_back(cv::Rect(10 * i, 5 * (i + j), 2, 3));
        }
    }
    cv::groupRectangles(rectangles, 2);

    return 0;
}

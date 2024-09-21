#include <opencv2/core.hpp>
#include <opencv2/aruco.hpp>

int main() {
    cv::Mat markerImage;
    auto dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_6X6_250);
    cv::aruco::drawMarker(dictionary, 23, 200, markerImage, 1);
    return 0;
}

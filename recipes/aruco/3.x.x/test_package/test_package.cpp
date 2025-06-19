#include <aruco/aruco.h>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>

#include <iostream>
#include <vector>

int main() {
    cv::Mat image = cv::Mat::zeros(600,600,CV_8UC3);

    aruco::MarkerDetector MDetector;
    MDetector.setDictionary("ARUCO_MIP_36h12");

    //detect
    std::vector<aruco::Marker> markers = MDetector.detect(image);

    return EXIT_SUCCESS;
}

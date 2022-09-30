#include <imutils/convenience.h>

#include <string>

int main() {
    cv::Mat image1 = cv::Mat::eye(256, 256, CV_8UC3);
    cv::Mat image2 = Convenience::translate(image1, 5.0, 3.0);

    return 0;
}

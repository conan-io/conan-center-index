#include <opencv2/video/background_segm.hpp>

int main() {
    auto bkg_subtractor_knn = cv::createBackgroundSubtractorKNN();

    return 0;
}

#include <opencv2/bgsegm.hpp>

int main() {
    auto bkg_subtractor = cv::bgsegm::createBackgroundSubtractorCNT();
    return 0;
}

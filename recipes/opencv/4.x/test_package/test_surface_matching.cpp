#include <opencv2/core.hpp>
#include <opencv2/surface_matching.hpp>

int main() {
    cv::ppf_match_3d::PPF3DDetector detector(0.03, 0.05);
    return 0;
}

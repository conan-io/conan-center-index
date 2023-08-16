#include <opencv2/xfeatures2d.hpp>

int main() {
    auto vgg = cv::xfeatures2d::VGG::create();
    return 0;
}

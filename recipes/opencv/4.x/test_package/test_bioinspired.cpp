#include <opencv2/bioinspired/retinafasttonemapping.hpp>

int main() {
    auto retina_tone_mapping = cv::bioinspired::RetinaFastToneMapping::create(cv::Size(10, 10));
    return 0;
}

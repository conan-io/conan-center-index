#include <opencv2/core.hpp>
#include <opencv2/fuzzy/fuzzy_F0_math.hpp>

int main() {
    cv::Mat image = cv::Mat::zeros(400, 400, CV_8UC3);
    cv::Mat output;
    cv::ft::FT02D_FL_process(image, 10, output);
    return 0;
}

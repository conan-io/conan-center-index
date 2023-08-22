#include <opencv2/dnn/dnn.hpp>

int main() {
    auto backends = cv::dnn::getAvailableBackends();
    return 0;
}

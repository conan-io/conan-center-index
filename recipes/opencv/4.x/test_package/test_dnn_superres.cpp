#include <opencv2/dnn_superres.hpp>

int main() {
    auto dnn_superres_impl = cv::dnn_superres::DnnSuperResImpl::create();
    return 0;
}

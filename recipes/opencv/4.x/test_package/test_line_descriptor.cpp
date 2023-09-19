#include <opencv2/line_descriptor/descriptor.hpp>

int main() {
    auto descriptor = cv::line_descriptor::BinaryDescriptor::createBinaryDescriptor();
    return 0;
}

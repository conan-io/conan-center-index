#include <opencv2/core.hpp>
#include <opencv2/optflow/sparse_matching_gpc.hpp>

int main() {
    auto tree = cv::optflow::GPCTree::create();
    return 0;
}

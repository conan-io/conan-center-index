#include <opencv2/datasets/ar_hmdb.hpp>

int main() {
    auto dataset = cv::datasets::AR_hmdb::create();
    return 0;
}

#include <opencv2/hdf/hdf5.hpp>

int main() {
    auto hdf5 = cv::hdf::open("test_package_hdf.h5");
    return 0;
}

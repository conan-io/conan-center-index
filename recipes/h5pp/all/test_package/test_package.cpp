#include <h5pp/h5pp.h>

int main() {
    using cplx = std::complex<double>;

    static_assert(h5pp::type::sfinae::has_data<std::vector<double>>() and
                  "h5pp ompile time type-checker failed. Could not properly detect class member data. Check that you are using a supported compiler!");

    std::string outputFilename = "test_package.h5";
    size_t      logLevel       = 1;
    h5pp::File  file(outputFilename, H5F_ACC_TRUNC | H5F_ACC_RDWR, logLevel);

    // Generate dummy data
    std::vector<cplx> vectorComplexWrite = {{-0.191154, 0.326211}, {0.964728, -0.712335}, {-0.0351791, -0.10264}, {0.177544, 0.99999}};

    // Write dummy data to file
    file.writeDataset(vectorComplexWrite, "vectorComplex");


    // Read dummy data from file
    auto vectorComplexRead = file.readDataset<std::vector<cplx>>("vectorComplex");

#if defined(H5PP_USE_FLOAT128)
    __float128 f128 = 6.28318530717958623199592693708837032318115234375;
    file.writeDataset(f128, "__float128");
    auto f128_read = file.readDataset<__float128>("__float128");
#endif

    return 0;
}

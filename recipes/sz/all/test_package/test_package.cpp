#include <SZ3/api/sz.hpp>
#ifdef SZ_WITH_HDF5
#include <H5Z_SZ3.hpp>
#endif
#include <vector>

int main() {
    std::vector<float> data(100, 1.0f);
    SZ3::Config conf(data.size());
    conf.errorBoundMode = SZ3::EB_ABS;
    conf.absErrorBound = 1e-3;
    size_t size = 0;
    char *compressed = SZ_compress(conf, data.data(), size);
    float *restored = SZ_decompress<float>(conf, compressed, size);
    delete[] compressed;
    delete[] restored;
#ifdef SZ_WITH_HDF5
    hid_t plist = H5Pcreate(H5P_DATASET_CREATE);
    herr_t ret = H5Pset_sz3(plist, H5Z_SZ3_ALGO_INTERP_LORENZO, H5Z_SZ3_EB_ABS, 1e-3, 0, 0, 0);
    H5Pclose(plist);
    return ret < 0;
#else
    return 0;
#endif
}

#include <SZ3/api/sz.hpp>
#include <SZ3/version.hpp>
#ifdef SZ_WITH_HDF5
#include <H5Z_SZ3.hpp>
#endif
#include <cstdio>
#include <vector>

int main() {
    std::vector<float> data(1000);
    for (size_t i = 0; i < data.size(); i++) data[i] = static_cast<float>(i % 37) * 0.25f;
    SZ3::Config conf(data.size());
    conf.errorBoundMode = SZ3::EB_ABS;
    conf.absErrorBound = 1e-3;
    size_t size = 0;
    char *compressed = SZ_compress(conf, data.data(), size);
    float *restored = SZ_decompress<float>(conf, compressed, size);
    std::printf("SZ3 %s: %zu bytes -> %zu bytes, first value %g\n", SZ3_VER, data.size() * sizeof(float), size,
                restored[1]);
    delete[] compressed;
    delete[] restored;
#ifdef SZ_WITH_HDF5
    hid_t plist = H5Pcreate(H5P_DATASET_CREATE);
    herr_t ret = H5Pset_sz3(plist, H5Z_SZ3_ALGO_INTERP_LORENZO, H5Z_SZ3_EB_ABS, 1e-3, 0, 0, 0);
    H5Pclose(plist);
    if (ret < 0) return 1;
#endif
    return 0;
}

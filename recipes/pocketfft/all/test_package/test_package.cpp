#include <pocketfft_hdronly.h>

#include <complex>
#include <vector>

using namespace pocketfft;

int main() {
  const int len = 16;
  shape_t shape{len};
  stride_t stride{sizeof(std::complex<float>)};
  shape_t axes = {0};
  std::vector<std::complex<float>> data(len), res(len);
  c2c(shape, stride, stride, axes, FORWARD, data.data(), res.data(), 1.f);
}

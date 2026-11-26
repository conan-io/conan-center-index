#include "ffft/FFTReal.h"

#include <cstdio>
#include <vector>

int main() {
    const long len = 64;
    ffft::FFTReal<float> fft_object(len);

    std::vector<float> x(len, 1.0f);
    std::vector<float> f(len, 0.0f);

    fft_object.do_fft(f.data(), x.data());
    fft_object.do_ifft(f.data(), x.data());
    fft_object.rescale(x.data());

    std::printf("fft-real: FFT/IFFT computed successfully on %ld samples\n", len);
    return 0;
}

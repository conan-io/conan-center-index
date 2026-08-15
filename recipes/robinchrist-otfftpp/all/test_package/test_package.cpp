#include "otfftpp/otfft.h"
#include <memory>
#include <iostream>

int main() {
    auto fft = OTFFT::createBluesteinFFT(13);

    if(OTFFT::builtWithOpenMP()) {
        std::cout << "  otfftpp: _OPENMP " << OTFFT::builtWithSSE() << "\n";
        std::cout << "  otfftpp: omp_get_max_threads " << OTFFT::getOpenMPMaxThreads() << "\n";
    }

    if(OTFFT::builtWithSSE()){
        std::cout << "  otfftpp: __SSE__ " << OTFFT::builtWithSSE() << "\n";
    }

    if(OTFFT::builtWithSSE3()){
        std::cout << "  otfftpp: __SSE3__ " << OTFFT::builtWithSSE3() << "\n";
    }

    if(OTFFT::builtWithAVX()){
        std::cout << "  otfftpp: __AVX__ " << OTFFT::builtWithAVX() << "\n";
    }

    if(OTFFT::builtWithAVX2()){
        std::cout << "  otfftpp: __AVX2__ " << OTFFT::builtWithAVX2() << "\n";
    }

    if(OTFFT::builtWithAVX512F()){
        std::cout << "  otfftpp: __AVX512F__ " << OTFFT::builtWithAVX512F() << "\n";
    }
}


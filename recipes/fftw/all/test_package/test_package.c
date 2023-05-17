#include "fftw3.h"

// switch API to match the precision option (fftw_|fftwf_|fftwl)
#if defined(ENABLE_SINGLE_PRECISION)
typedef float real_t;
#define FFTW_MANGLE(name) FFTW_MANGLE_FLOAT(name)
#elif defined(ENABLE_LONG_DOUBLE_PRECISION)
typedef long double real_t;
#define FFTW_MANGLE(name) FFTW_MANGLE_LONG_DOUBLE(name)
#else
typedef double real_t;
#define FFTW_MANGLE(name) FFTW_MANGLE_DOUBLE(name)
#endif

int main() {
    long size = 256;
    real_t* input = FFTW_MANGLE(alloc_real)(size);
    FFTW_MANGLE(complex)* output = FFTW_MANGLE(alloc_complex)(size);
    FFTW_MANGLE(plan) plan = (FFTW_MANGLE(plan_dft_r2c_1d)(
          size, input, output, FFTW_ESTIMATE));
    FFTW_MANGLE(execute)(plan);
    FFTW_MANGLE(destroy_plan)(plan);
    FFTW_MANGLE(free)(output);
    FFTW_MANGLE(free)(input);
    return 0;
}

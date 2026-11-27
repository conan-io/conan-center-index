#include <stdio.h>

#ifdef TEST_FLOAT
#include <pffft/pffft.h>
#else
#include <pffft/pffft_double.h>
#endif

#ifdef TEST_PFFASTCONV
#include <pffft/pffastconv.h>
#endif

#ifdef TEST_PFDSP
#include <pffft/pf_carrier.h>
#endif

#define N 64

int main(void) {
#ifdef TEST_FLOAT
    PFFFT_Setup *setup = pffft_new_setup(N, PFFFT_REAL);
    float *buf = (float *)pffft_aligned_malloc(N * sizeof(float));
    int i;
    for (i = 0; i < N; ++i) buf[i] = (float)i;
    pffft_transform_ordered(setup, buf, buf, NULL, PFFFT_FORWARD);
    printf("pffft  %s, simd size %d\n", pffft_simd_arch(), pffft_simd_size());
    pffft_aligned_free(buf);
    pffft_destroy_setup(setup);
#else
    PFFFTD_Setup *setup = pffftd_new_setup(N, PFFFT_REAL);
    double *buf = (double *)pffft_aligned_malloc(N * sizeof(double));
    int i;
    for (i = 0; i < N; ++i) buf[i] = (double)i;
    pffftd_transform_ordered(setup, buf, buf, NULL, PFFFT_FORWARD);
    printf("pffftd %s, simd size %d\n", pffftd_simd_arch(), pffftd_simd_size());
    pffft_aligned_free(buf);
    pffftd_destroy_setup(setup);
#endif

#ifdef TEST_PFFASTCONV
    printf("pffastconv simd size %d\n", pffastconv_simd_size());
#endif

#ifdef TEST_PFDSP
    {
        float dc[8];
        generate_dc_f(dc, 4);
        printf("pfdsp dc %g\n", dc[0]);
    }
#endif

    return 0;
}

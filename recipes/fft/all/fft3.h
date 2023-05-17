#pragma once

#ifndef __FFT_FFT3_H_F55B14B4_B254_4440_B623_B689DEFA3E0D__
#define __FFT_FFT3_H_F55B14B4_B254_4440_B623_B689DEFA3E0D__

#include "fft_export.h"

#ifdef __cplusplus
extern "C" {
#endif

FFT_EXPORT void cdft3d(int, int, int, int, double ***, double *, int *, double *);
FFT_EXPORT void rdft3d(int, int, int, int, double ***, double *, int *, double *);
FFT_EXPORT void rdft3dsort(int, int, int, int, double ***);
FFT_EXPORT void ddct3d(int, int, int, int, double ***, double *, int *, double *);
FFT_EXPORT void ddst3d(int, int, int, int, double ***, double *, int *, double *);

#ifdef __cplusplus
}
#endif

#endif /* __FFT_FFT3_H_F55B14B4_B254_4440_B623_B689DEFA3E0D__ */

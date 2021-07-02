#pragma once

#ifndef __FFT_FFT2_H_F6EDD639_4BBB_4536_9F32_C7DFEC1608A3__
#define __FFT_FFT2_H_F6EDD639_4BBB_4536_9F32_C7DFEC1608A3__

#include "fft_export.h"

#ifdef __cplusplus
extern "C" {
#endif

FFT_EXPORT void cdft2d(int, int, int, double **, double *, int *, double *);
FFT_EXPORT void rdft2d(int, int, int, double **, double *, int *, double *);
FFT_EXPORT void rdft2dsort(int, int, int, double **);
FFT_EXPORT void ddct2d(int, int, int, double **, double *, int *, double *);
FFT_EXPORT void ddst2d(int, int, int, double **, double *, int *, double *);

#ifdef __cplusplus
}
#endif

#endif /* __FFT_FFT2_H_F6EDD639_4BBB_4536_9F32_C7DFEC1608A3__ */

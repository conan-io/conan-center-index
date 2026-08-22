#pragma once

#ifndef __FFT_FFT_H_796A834A_D06E_4C88_A15C_E611857B108F__
#define __FFT_FFT_H_796A834A_D06E_4C88_A15C_E611857B108F__

#include "fft_export.h"

#ifdef __cplusplus
extern "C" {
#endif

FFT_EXPORT void cdft(int, int, double *, int *, double *);
FFT_EXPORT void rdft(int, int, double *, int *, double *);
FFT_EXPORT void ddct(int, int, double *, int *, double *);
FFT_EXPORT void ddst(int, int, double *, int *, double *);
FFT_EXPORT void dfct(int, double *, double *, int *, double *);
FFT_EXPORT void dfst(int, double *, double *, int *, double *);

#ifdef __cplusplus
}
#endif

#endif /* __FFT_FFT_H_796A834A_D06E_4C88_A15C_E611857B108F__ */

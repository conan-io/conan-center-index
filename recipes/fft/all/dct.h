#pragma once

#ifndef __FFT_DCT_H_AC3FBB1E_47B8_49E2_8271_1E44DAB78490__
#define __FFT_DCT_H_AC3FBB1E_47B8_49E2_8271_1E44DAB78490__

#include "fft_export.h"

#ifdef __cplusplus
extern "C" {
#endif

FFT_EXPORT void ddct8x8s(int isgn, double **a);
FFT_EXPORT void ddct16x16s(int isgn, double **a);

#ifdef __cplusplus
}
#endif

#endif /* __FFT_DCT_H_AC3FBB1E_47B8_49E2_8271_1E44DAB78490__ */

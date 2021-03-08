// SSHT package to perform spin spherical harmonic transforms
// Copyright (C) 2011  Jason McEwen
// See LICENSE.txt for license details

/*!
 * \file ssht_test.c
 * Applies SSHT algorithms to perform inverse and forward spherical
 * harmonic transforms (respectively) to check that the original
 * signal is reconstructed exactly (to numerical precision).  Test is
 * performed on a random signal with harmonic coefficients uniformly
 * sampled from (-1,1).
 *
 * Usage: ssht_test B spin [B0], e.g. ssht_test 64 2 32
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */

#include <tgmath.h> // Must be before fftw3.h
#include <fftw3.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <ssht/ssht.h>

#define NREPEAT 5
#define MAX(a, b) ((a) > (b) ? (a) : (b))

double ran2_dp(int idum);
void ssht_test_gen_flm_complex(complex double* flm, int L, int spin, int seed);
void ssht_test_gen_flm_real(complex double* flm, int L, int seed);
void ssht_test_gen_lb_flm_complex(complex double* flm, int L_zero, int L, int spin, int seed);
void ssht_test_gen_lb_flm_real(complex double* flm, int L0, int L, int seed);

/*!
 * Test for null vector
 *
 * \param[in]  X vector of complex double
 * \param[in]  n length of X.
 * \retval     Y returns int 0 if all zeros, 1 if non-zero
 *             i.e. 0 = fail, 1 = pass.
 */

int null_test(const complex double *X, int n)
{
  int Y = 0;
  for(int i = 0; i < n; ++i){ if(cabs(X[i]) != 0.0){ Y = 1; i = n; } }
  return Y;
}

/*!
 * Test for nan vector
 *
 * \param[in]  X vector of complex double
 * \param[in]  n length of X.
 * \retval     Y returns int 1 if no nans, 0 if nan entires exist.
 *             i.e. 0 = fail, 1 = pass.
 */

int nan_test(const complex double *X, int n)
{
  int Y = 1;
  for(int i = 0; i < n; ++i){ if(X[i] != X[i]){ Y = 0; i = n; } }
  return Y;
}

int main(int argc, char* argv[])
{

  complex double *flm_orig, *flm_syn;
  complex double *f_mw, *f_mw_ss, *f_gl, *f_dh;
  double *f_mw_real, *f_mw_ss_real, *f_gl_real, *f_dh_real;
  complex double *f_mw_lb, *f_mw_lb_ss;
  double *f_mw_lb_real, *f_mw_lb_ss_real;

  complex double *f_mw_pole, *f_mw_ss_pole;
  complex double f_mw_sp, f_mw_ss_np, f_mw_ss_sp;
  double *f_mw_real_pole, *f_mw_ss_real_pole;
  double f_mw_real_sp, f_mw_ss_real_sp, f_mw_ss_real_np, phi_sp, phi_np;

  ssht_dl_method_t dl_method = SSHT_DL_RISBO;
  int L = 128;
  int L0 = 32;
  int spin = 0;
  int irepeat;
  int seed = 1;
  int verbosity = 0;
  int i;
  double tmp;

  clock_t time_start, time_end;
  double errors_mw[NREPEAT];
  double errors_mw_lb[NREPEAT];
  double errors_mw_pole[NREPEAT];
  double errors_mw_ss[NREPEAT];
  double errors_mw_lb_ss[NREPEAT];
  double errors_mw_ss_pole[NREPEAT];
  double errors_gl[NREPEAT];
  double errors_dh[NREPEAT];
  double errors_mw_real[NREPEAT];
  double errors_mw_lb_real[NREPEAT];
  double errors_mw_real_pole[NREPEAT];
  double errors_mw_ss_real[NREPEAT];
  double errors_mw_lb_ss_real[NREPEAT];
  double errors_mw_ss_real_pole[NREPEAT];
  double errors_gl_real[NREPEAT];
  double errors_dh_real[NREPEAT];
  double durations_forward_mw[NREPEAT];
  double durations_inverse_mw[NREPEAT];
  double durations_forward_mw_lb[NREPEAT];
  double durations_inverse_mw_lb[NREPEAT];
  double durations_forward_mw_pole[NREPEAT];
  double durations_inverse_mw_pole[NREPEAT];
  double durations_forward_mw_ss[NREPEAT];
  double durations_inverse_mw_ss[NREPEAT];
  double durations_forward_mw_lb_ss[NREPEAT];
  double durations_inverse_mw_lb_ss[NREPEAT];
  double durations_forward_mw_ss_pole[NREPEAT];
  double durations_inverse_mw_ss_pole[NREPEAT];
  double durations_forward_gl[NREPEAT];
  double durations_inverse_gl[NREPEAT];
  double durations_forward_dh[NREPEAT];
  double durations_inverse_dh[NREPEAT];
  double durations_forward_mw_real[NREPEAT];
  double durations_inverse_mw_real[NREPEAT];
  double durations_forward_mw_lb_real[NREPEAT];
  double durations_inverse_mw_lb_real[NREPEAT];
  double durations_forward_mw_real_pole[NREPEAT];
  double durations_inverse_mw_real_pole[NREPEAT];
  double durations_forward_mw_ss_real[NREPEAT];
  double durations_inverse_mw_ss_real[NREPEAT];
  double durations_forward_mw_lb_ss_real[NREPEAT];
  double durations_inverse_mw_lb_ss_real[NREPEAT];
  double durations_forward_mw_ss_real_pole[NREPEAT];
  double durations_inverse_mw_ss_real_pole[NREPEAT];
  double durations_forward_gl_real[NREPEAT];
  double durations_inverse_gl_real[NREPEAT];
  double durations_forward_dh_real[NREPEAT];
  double durations_inverse_dh_real[NREPEAT];

  // Parse problem sizes.
  L = 64;
  spin = 0;
  if (argc > 1) {
    L = atoi(argv[1]);
  } else {
    printf("\n");
    printf("Choosing default L = 128\n");
  }
  if (argc > 2) {
    spin = atoi(argv[2]);
  } else {
    printf("\n");
    printf("Choosing default s = 0\n");
  }
  if (argc > 3)
    L0 = atoi(argv[3]);

  // Allocate memory.
  flm_orig = (complex double*)calloc(L * L, sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(flm_orig)
  flm_syn = (complex double*)calloc(L * L, sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(flm_syn)
  f_mw = (complex double*)calloc(L * (2 * L - 1), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw)
  f_mw_lb = (complex double*)calloc(L * (2 * L - 1), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw)
  f_mw_ss = (complex double*)calloc((L + 1) * (2 * L), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss)
  f_mw_lb_ss = (complex double*)calloc((L + 1) * (2 * L), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss)
  f_mw_pole = (complex double*)calloc((L - 1) * (2 * L - 1), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_pole)
  f_mw_ss_pole = (complex double*)calloc((L - 1) * (2 * L), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss_pole)
  f_gl = (complex double*)calloc(L * (2 * L - 1), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_gl)
  f_dh = (complex double*)calloc((2 * L) * (2 * L - 1), sizeof(complex double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_dh)
  f_mw_real = (double*)calloc(L * (2 * L - 1), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_real)
  f_mw_lb_real = (double*)calloc(L * (2 * L - 1), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_real)
  f_mw_ss_real = (double*)calloc((L + 1) * (2 * L), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss_real)
  f_mw_lb_ss_real = (double*)calloc((L + 1) * (2 * L), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss_real)
  f_mw_real_pole = (double*)calloc((L - 1) * (2 * L - 1), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_real_pole)
  f_mw_ss_real_pole = (double*)calloc((L - 1) * (2 * L), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_mw_ss_real_pole)
  f_gl_real = (double*)calloc(L * (2 * L - 1), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_gl_real)
  f_dh_real = (double*)calloc((2 * L) * (2 * L - 1), sizeof(double));
  SSHT_ERROR_MEM_ALLOC_CHECK(f_dh_real)

  // Write program name.
  printf("\n");
  printf("SSHT test program (C implementation)\n");
  printf("================================================================\n");

  // Run algorithm error and timing tests.
  for (irepeat = 0; irepeat < NREPEAT; irepeat++) {

    // If spin=0 run tests on algorithms optimised for real spin=0 signal.
    if (spin == 0) {

      // =========================================================================
      // DH real spin=0
      printf("DH real test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_dh_inverse_sov_real(f_dh_real, flm_orig, L, verbosity);
      time_end = clock();
      durations_inverse_dh_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_dh_forward_sov_real(flm_syn, f_dh_real, L, verbosity);
      time_end = clock();
      durations_forward_dh_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_dh_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_dh_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_dh_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_dh_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_dh_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_dh_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // GL real spin=0
      printf("GL real test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_gl_inverse_sov_real(f_gl_real, flm_orig, L, verbosity);
      time_end = clock();
      durations_inverse_gl_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_gl_forward_sov_real(flm_syn, f_gl_real, L, verbosity);
      time_end = clock();
      durations_forward_gl_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_gl_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_gl_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_gl_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_gl_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_gl_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_gl_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW real spin=0
      printf("MW real test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_mw_inverse_sov_sym_real(f_mw_real, flm_orig, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_forward_sov_conv_sym_real(flm_syn, f_mw_real, L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW real spin=0 with lower band-limit
      printf("MW real (lower band-limit) test no. %d\n", irepeat);

      ssht_test_gen_lb_flm_real(flm_orig, L0, L, seed);
      time_start = clock();
      ssht_core_mw_lb_inverse_sov_sym_real(f_mw_lb_real, flm_orig, L0, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_lb_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_lb_forward_sov_conv_sym_real(flm_syn, f_mw_lb_real, L0, L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_lb_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_lb_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_lb_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_lb_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_lb_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_lb_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_lb_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW real spin=0 pole
      printf("MW real pole test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_mw_inverse_sov_sym_real_pole(f_mw_real_pole,
          &f_mw_real_sp,
          flm_orig, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_real_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_forward_sov_conv_sym_real_pole(flm_syn, f_mw_real_pole,
          f_mw_real_sp,
          L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_real_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_real_pole[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_real_pole[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_real_pole[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_real_pole[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_real_pole[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_real_pole[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW SS real spin=0
      printf("MW SS real test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_mw_inverse_sov_sym_ss_real(f_mw_ss_real, flm_orig, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_ss_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_forward_sov_conv_sym_ss_real(flm_syn, f_mw_ss_real, L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_ss_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_ss_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_ss_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_ss_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_ss_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_ss_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_ss_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW SS real spin=0 with lower band-limit
      printf("MW SS real (lower band-limit) test no. %d\n", irepeat);

      ssht_test_gen_lb_flm_real(flm_orig, L0, L, seed);
      time_start = clock();
      ssht_core_mw_lb_inverse_sov_sym_ss_real(f_mw_lb_ss_real, flm_orig, L0, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_lb_ss_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_lb_forward_sov_conv_sym_ss_real(flm_syn, f_mw_lb_ss_real, L0, L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_lb_ss_real[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_lb_ss_real[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_lb_ss_real[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_lb_ss_real[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_lb_ss_real[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_lb_ss_real[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_lb_ss_real[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

      // =========================================================================
      // MW SS real spin=0 pole
      printf("MW SS real pole test no. %d\n", irepeat);

      ssht_test_gen_flm_real(flm_orig, L, seed);
      time_start = clock();
      ssht_core_mw_inverse_sov_sym_ss_real_pole(f_mw_ss_real_pole,
          &f_mw_ss_real_np,
          &f_mw_ss_real_sp,
          flm_orig, L,
          dl_method, verbosity);
      time_end = clock();
      durations_inverse_mw_ss_real_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      time_start = clock();
      ssht_core_mw_forward_sov_conv_sym_ss_real_pole(flm_syn,
          f_mw_ss_real_pole,
          f_mw_ss_real_np,
          f_mw_ss_real_sp,
          L,
          dl_method, verbosity);
      time_end = clock();
      durations_forward_mw_ss_real_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

      errors_mw_ss_real_pole[irepeat] = 0.0;
      for (i = 0; i < L * L; i++)
        errors_mw_ss_real_pole[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_ss_real_pole[irepeat]);

      printf(" duration_inverse (s) = %40.4f\n",
          durations_inverse_mw_ss_real_pole[irepeat]);
      printf(" duration_forward (s) = %40.4f\n",
          durations_forward_mw_ss_real_pole[irepeat]);
      printf(" error                = %40.5e\n\n",
          errors_mw_ss_real_pole[irepeat]);

      //! Null and Nan Tests!
      printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
      printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients
    }

    // =========================================================================
    // DH
    printf("DH test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_dh_inverse_sov(f_dh, flm_orig, L, spin, verbosity);
    time_end = clock();
    durations_inverse_dh[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_dh_forward_sov(flm_syn, f_dh, L, spin, verbosity);
    time_end = clock();
    durations_forward_dh[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_dh[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_dh[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_dh[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_dh[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_dh[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_dh[irepeat]);

    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // GL
    printf("GL test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_gl_inverse_sov(f_gl, flm_orig, L, spin, verbosity);
    time_end = clock();
    durations_inverse_gl[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_gl_forward_sov(flm_syn, f_gl, L, spin, verbosity);
    time_end = clock();
    durations_forward_gl[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_gl[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_gl[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_gl[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_gl[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_gl[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_gl[irepeat]);

    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW
    printf("MW test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_mw_inverse_sov_sym(f_mw, flm_orig, L, spin, dl_method, verbosity);
    time_end = clock();
    durations_inverse_mw[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_forward_sov_conv_sym(flm_syn, f_mw, L, spin, dl_method, verbosity);
    time_end = clock();
    durations_forward_mw[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw[irepeat]);
    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW with lower band-limit
    printf("MW lower band-limit test no. %d\n", irepeat);

    ssht_test_gen_lb_flm_complex(flm_orig, L0, L, spin, seed);

    time_start = clock();
    ssht_core_mw_lb_inverse_sov_sym(f_mw_lb, flm_orig, L0, L, spin, dl_method, verbosity);
    time_end = clock();
    durations_inverse_mw_lb[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_lb_forward_sov_conv_sym(flm_syn, f_mw_lb, L0, L, spin, dl_method, verbosity);
    time_end = clock();
    durations_forward_mw_lb[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw_lb[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw_lb[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_lb[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw_lb[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw_lb[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw_lb[irepeat]);

        //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW pole
    printf("MW pole test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_mw_inverse_sov_sym_pole(f_mw_pole, &f_mw_sp, &phi_sp,
        flm_orig, L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_inverse_mw_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_forward_sov_conv_sym_pole(flm_syn, f_mw_pole, f_mw_sp, phi_sp,
        L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_forward_mw_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw_pole[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw_pole[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_pole[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw_pole[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw_pole[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw_pole[irepeat]);

    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW SS
    printf("MW SS test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_mw_inverse_sov_sym_ss(f_mw_ss, flm_orig, L, spin,
        dl_method, verbosity);
    //ssht_core_mwdirect_inverse_ss(f_mw_ss, flm_orig, L, spin, verbosity);
    time_end = clock();
    durations_inverse_mw_ss[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_forward_sov_conv_sym_ss(flm_syn, f_mw_ss, L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_forward_mw_ss[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw_ss[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw_ss[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_ss[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw_ss[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw_ss[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw_ss[irepeat]);

    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW SS with lower band-limit
    printf("MW SS (lower band-limit) test no. %d\n", irepeat);

    ssht_test_gen_lb_flm_complex(flm_orig, L0, L, spin, seed);
    time_start = clock();
    ssht_core_mw_lb_inverse_sov_sym_ss(f_mw_lb_ss, flm_orig, L0, L, spin,
        dl_method, verbosity);

    time_end = clock();
    durations_inverse_mw_lb_ss[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_lb_forward_sov_conv_sym_ss(flm_syn, f_mw_lb_ss, L0, L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_forward_mw_lb_ss[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw_lb_ss[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw_lb_ss[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_lb_ss[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw_lb_ss[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw_lb_ss[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw_lb_ss[irepeat]);

    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients

    // =========================================================================
    // MW SS pole
    printf("MW SS pole test no. %d\n", irepeat);

    ssht_test_gen_flm_complex(flm_orig, L, spin, seed);
    time_start = clock();
    ssht_core_mw_inverse_sov_sym_ss_pole(f_mw_ss_pole,
        &f_mw_ss_np, &phi_np,
        &f_mw_ss_sp, &phi_sp,
        flm_orig, L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_inverse_mw_ss_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    time_start = clock();
    ssht_core_mw_forward_sov_conv_sym_ss_pole(flm_syn, f_mw_ss_pole,
        f_mw_ss_np, phi_np,
        f_mw_ss_sp, phi_sp,
        L, spin,
        dl_method, verbosity);
    time_end = clock();
    durations_forward_mw_ss_pole[irepeat] = (time_end - time_start) / (double)CLOCKS_PER_SEC;

    errors_mw_ss_pole[irepeat] = 0.0;
    for (i = 0; i < L * L; i++)
      errors_mw_ss_pole[irepeat] = MAX(cabs(flm_orig[i] - flm_syn[i]), errors_mw_ss_pole[irepeat]);

    printf(" duration_inverse (s) = %40.4f\n",
        durations_inverse_mw_ss_pole[irepeat]);
    printf(" duration_forward (s) = %40.4f\n",
        durations_forward_mw_ss_pole[irepeat]);
    printf(" error                = %40.5e\n\n",
        errors_mw_ss_pole[irepeat]);
    //! Null and Nan Tests!
    printf("  - Null, Nan test result (Input Harmonic Coefficients) : %d, %d\n", null_test(flm_orig, L*L), nan_test(flm_orig, L*L)); //! Harmonic Coefficients
    printf("  - Null, Nan test result (Output Harmonic Coefficients) : %d, %d\n", null_test(flm_syn, L*L), nan_test(flm_syn, L*L)); //! Harmonic Coefficients
  }

  // =========================================================================
  // Summarise results

  printf("================================================================\n");
  printf("Summary\n\n");
  printf("NREPEAT               = %40d\n", NREPEAT);
  printf("L                     = %40d\n", L);
  printf("spin                  = %40d\n\n", spin);

  if (spin == 0) {

    printf("DH real\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_dh_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_dh_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_dh_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("GL real\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_gl_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_gl_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_gl_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW real\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW real with lower band-limit\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_lb_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_lb_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_lb_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW real pole\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_real_pole[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_real_pole[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_real_pole[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW SS real\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_lb_ss_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_lb_ss_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_lb_ss_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW SS real with lower band-limit\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_lb_ss_real[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_lb_ss_real[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_lb_ss_real[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

    printf("MW SS real pole\n");
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_forward_mw_ss_real_pole[i];
    printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += durations_inverse_mw_ss_real_pole[i];
    printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
    tmp = 0.0;
    for (i = 0; i < NREPEAT; i++)
      tmp += errors_mw_ss_real_pole[i];
    printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);
  }

  printf("DH\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_dh[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_dh[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_dh[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("GL\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_gl[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_gl[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_gl[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW with lower band-limit\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw_lb[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw_lb[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw_lb[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW pole\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw_pole[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw_pole[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw_pole[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW SS\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw_ss[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw_ss[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw_ss[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW SS with lower band-limit\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw_lb_ss[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw_lb_ss[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw_lb_ss[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  printf("MW SS pole\n");
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_forward_mw_ss_pole[i];
  printf(" Average forward transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += durations_inverse_mw_ss_pole[i];
  printf(" Average inverse transform time (s) = %26.4f\n", tmp / (double)NREPEAT);
  tmp = 0.0;
  for (i = 0; i < NREPEAT; i++)
    tmp += errors_mw_ss_pole[i];
  printf(" Average max error                  = %26.5e\n\n", tmp / (double)NREPEAT);

  // Free memory.
  free(flm_orig);
  free(flm_syn);
  free(f_mw);
  free(f_mw_lb);
  free(f_mw_ss);
  free(f_mw_lb_ss);
  free(f_mw_real);
  free(f_mw_lb_real);
  free(f_mw_ss_real);
  free(f_mw_lb_ss_real);
  free(f_mw_pole);
  free(f_mw_ss_pole);
  free(f_mw_real_pole);
  free(f_mw_ss_real_pole);
  free(f_gl);
  free(f_gl_real);
  free(f_dh);
  free(f_dh_real);

  return 0;
}

/*!
 * Generate random spherical harmonic coefficients of a real spin=0
 * signal.
 *
 * \param[out] flm Random spherical harmonic coefficients generated.
 * \param[in] L Harmonic band-limit.
 * \param[in] seed Integer seed required for random number generator.
 * \retval none
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */
void ssht_test_gen_flm_real(complex double* flm, int L, int seed)
{

  int el, m, msign, i, i_op;

  for (el = 0; el < L; el++) {
    m = 0;
    ssht_sampling_elm2ind(&i, el, m);
    flm[i] = (2.0 * ran2_dp(seed) - 1.0);
    for (m = 1; m <= el; m++) {
      ssht_sampling_elm2ind(&i, el, m);
      flm[i] = (2.0 * ran2_dp(seed) - 1.0) + I * (2.0 * ran2_dp(seed) - 1.0);
      ssht_sampling_elm2ind(&i_op, el, -m);
      msign = m & 1;
      msign = 1 - msign - msign; // (-1)^m
      flm[i_op] = msign * conj(flm[i]);
    }
  }
}

/*!
 * Generate random spherical harmonic coefficients of a real spin=0
 * signal with lower band-limit.
 *
 * \param[out] flm Random spherical harmonic coefficients generated.
 * \param[in] L0 Lower harmonic band-limit.
 * \param[in] L Upper harmonic band-limit.
 * \param[in] seed Integer seed required for random number generator.
 * \retval none
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */
void ssht_test_gen_lb_flm_real(complex double* flm, int L0, int L, int seed)
{

  int el, m, msign, i, i_op;

  for (el = 0; el < L0; el++) {
    m = 0;
    ssht_sampling_elm2ind(&i, el, m);
    flm[i] = 0.0;
    for (m = 1; m <= el; m++) {
      ssht_sampling_elm2ind(&i, el, m);
      flm[i] = 0.0;
      ssht_sampling_elm2ind(&i, el, -m);
      flm[i] = 0.0;
    }
  }

  for (el = L0; el < L; el++) {
    m = 0;
    ssht_sampling_elm2ind(&i, el, m);
    flm[i] = (2.0 * ran2_dp(seed) - 1.0);
    for (m = 1; m <= el; m++) {
      ssht_sampling_elm2ind(&i, el, m);
      flm[i] = (2.0 * ran2_dp(seed) - 1.0) + I * (2.0 * ran2_dp(seed) - 1.0);
      ssht_sampling_elm2ind(&i_op, el, -m);
      msign = m & 1;
      msign = 1 - msign - msign; // (-1)^m
      flm[i_op] = msign * conj(flm[i]);
    }
  }
}

/*!
 * Generate random spherical harmonic coefficients of a complex
 * signal.
 *
 * \param[out] flm Random spherical harmonic coefficients generated.
 * \param[in] L Harmonic band-limit.
 * \param[in] spin Spin number.
 * \param[in] seed Integer seed required for random number generator.
 * \retval none
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */
void ssht_test_gen_flm_complex(complex double* flm, int L, int spin, int seed)
{

  int i, i_lo;

  ssht_sampling_elm2ind(&i_lo, abs(spin), 0);
  for (i = i_lo; i < L * L; i++)
    flm[i] = (2.0 * ran2_dp(seed) - 1.0) + I * (2.0 * ran2_dp(seed) - 1.0);
}

/*!
 * Generate random spherical harmonic coefficients of a complex
 * signal with lower band-limit.
 *
 * \param[out] flm Random spherical harmonic coefficients generated.
 * \param[in] L0 Lower harmonic band-limit.
 * \param[in] L Upper harmonic band-limit.
 * \param[in] spin Spin number.
 * \param[in] seed Integer seed required for random number generator.
 * \retval none
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */
void ssht_test_gen_lb_flm_complex(complex double* flm, int L0, int L, int spin, int seed)
{

  int i, i_lo;

  ssht_sampling_elm2ind(&i_lo, abs(spin), 0);
  for (i = 0; i < MAX(i_lo, L0 * L0); i++){ flm[i] = 0.0; }
  for (i = MAX(i_lo, L0 * L0); i < L * L; i++){ flm[i] = (2.0 * ran2_dp(seed) - 1.0) + I * (2.0 * ran2_dp(seed) - 1.0);}

}

/*!
 * Generate uniform deviate in range [0,1) given seed. (Using double
 * precision.)
 *
 * \note Uniform deviate (Num rec 1992, chap 7.1), original routine
 * said to be 'perfect'.
 *
 * \param[in] idum Seed.
 * \retval ran_dp Generated uniform deviate.
 *
 * \author <a href="http://www.jasonmcewen.org">Jason McEwen</a>
 */
double ran2_dp(int idum)
{

  int IM1 = 2147483563, IM2 = 2147483399, IMM1 = IM1 - 1,
      IA1 = 40014, IA2 = 40692, IQ1 = 53668, IQ2 = 52774, IR1 = 12211, IR2 = 3791,
      NTAB = 32, NDIV = 1 + IMM1 / NTAB;

  double AM = 1. / IM1, EPS = 1.2e-7, RNMX = 1. - EPS;
  int j, k;
  static int iv[32], iy, idum2 = 123456789;
  // N.B. in C static variables are initialised to 0 by default.

  if (idum <= 0) {
    idum = (-idum > 1 ? -idum : 1); // max(-idum,1);
    idum2 = idum;
    for (j = NTAB + 8; j >= 1; j--) {
      k = idum / IQ1;
      idum = IA1 * (idum - k * IQ1) - k * IR1;
      if (idum < 0)
        idum = idum + IM1;
      if (j < NTAB)
        iv[j - 1] = idum;
    }
    iy = iv[0];
  }
  k = idum / IQ1;
  idum = IA1 * (idum - k * IQ1) - k * IR1;
  if (idum < 0)
    idum = idum + IM1;
  k = idum2 / IQ2;
  idum2 = IA2 * (idum2 - k * IQ2) - k * IR2;
  if (idum2 < 0)
    idum2 = idum2 + IM2;
  j = 1 + iy / NDIV;
  iy = iv[j - 1] - idum2;
  iv[j - 1] = idum;
  if (iy < 1)
    iy = iy + IMM1;
  return (AM * iy < RNMX ? AM * iy : RNMX); // min(AM*iy,RNMX);
}

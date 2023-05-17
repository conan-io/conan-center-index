/*      driver for chkder example. */

#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <cminpack.h>
#define real __cminpack_real__

/* the following struct defines the data points */
typedef struct  {
    int m;
    real *y;
#ifdef BOX_CONSTRAINTS
    real *xmin;
    real *xmax;
#endif
} fcndata_t;

int fcn(void *p, int m, int n, const real *x, real *fvec,
	 real *fjac, int ldfjac, int iflag);

int main()
{
#if defined(__MINGW32__) || (defined(_MSC_VER) && (_MSC_VER < 1900))
  _set_output_format(_TWO_DIGIT_EXPONENT);
#endif
  int i, ldfjac;
  real x[3], fvec[15], fjac[15*3], xp[3], fvecp[15], 
    err[15];
  const int m = 15;
  const int n = 3;
  /* auxiliary data (e.g. measurements) */
  real y[15] = {1.4e-1, 1.8e-1, 2.2e-1, 2.5e-1, 2.9e-1, 3.2e-1, 3.5e-1,
                  3.9e-1, 3.7e-1, 5.8e-1, 7.3e-1, 9.6e-1, 1.34, 2.1, 4.39};
#ifdef BOX_CONSTRAINTS
  real xmin[3] = {0., 0.1, 0.5};
  real xmax[3] = {2., 1.5, 2.3};
#endif
  fcndata_t data;
  data.m = m;
  data.y = y;
#ifdef BOX_CONSTRAINTS
  data.xmin = xmin;
  data.xmax = xmax;
#endif

  /*      the following values should be suitable for */
  /*      checking the jacobian matrix. */

  x[0] = 9.2e-1;
  x[1] = 1.3e-1;
  x[2] = 5.4e-1;

  ldfjac = 15;

  /* compute xp from x */
  __cminpack_func__(chkder)(m, n, x, NULL, NULL, ldfjac, xp, NULL, 1, NULL);
  /* compute fvec at x (all components of fvec should be != 0).*/
  fcn(&data, m, n, x, fvec, NULL, ldfjac, 1);
  /* compute fjac at x */
  fcn(&data, m, n, x, NULL, fjac, ldfjac, 2);
  /* compute fvecp at xp (all components of fvecp should be != 0)*/
  fcn(&data, m, n, xp, fvecp, NULL, ldfjac, 1);
  /* check Jacobian, put the result in err */
  __cminpack_func__(chkder)(m, n, x, fvec, fjac, ldfjac, NULL, fvecp, 2, err);
  /* Output values:
     err[i] = 1.: i-th gradient is correct
     err[i] = 0.: i-th gradient is incorrect
     err[I] > 0.5: i-th gradient is probably correct
  */

  for (i=0; i<m; ++i) {
    fvecp[i] = fvecp[i] - fvec[i];
  }
  printf("\n      fvec\n");  
  for (i=0; i<m; ++i) {
    printf("%s%15.7g",i%3==0?"\n     ":"", (double)fvec[i]);
  }
  printf("\n      fvecp - fvec\n");  
  for (i=0; i<m; ++i) {
    printf("%s%15.7g",i%3==0?"\n     ":"", (double)fvecp[i]);
  }
  printf("\n      err\n");  
  for (i=0; i<m; ++i) {
    printf("%s%15.7g",i%3==0?"\n     ":"", (double)err[i]);
  }
  printf("\n");
  return 0;
}

int fcn(void *p, int m, int n, const real *x, real *fvec,
	 real *fjac, int ldfjac, int iflag)
{
  /*      subroutine fcn for chkder example. */
  assert(m == 15 && n == 3);
  int i;
  real tmp1, tmp2, tmp3, tmp4;
  const real *y = ((fcndata_t*)p)->y;
#ifdef BOX_CONSTRAINTS
  const real *xmin = ((fcndata_t*)p)->xmin;
  const real *xmax = ((fcndata_t*)p)->xmax;
  int j;
  real xb[3];
  real jacfac[3];

  for (j = 0; j < 3; ++j) {
    real xmiddle = (xmin[j]+xmax[j])/2.;
    real xwidth = (xmax[j]-xmin[j])/2.;
    real th =  tanh((x[j]-xmiddle)/xwidth);
    xb[j] = xmiddle + th * xwidth;
    jacfac[j] = 1. - th * th;
  }
  x = xb;
#endif

  if (iflag == 0) {
    /*      insert print statements here when nprint is positive. */
    /* if the nprint parameter to lmder is positive, the function is
       called every nprint iterations with iflag=0, so that the
       function may perform special operations, such as printing
       residuals. */
    return 0;
  }

  if (iflag != 2) {
    /* compute residuals */
    for (i=0; i < 15; ++i) {
      tmp1 = i + 1;
      tmp2 = 15 - i;
      tmp3 = (i > 7) ? tmp2 : tmp1;
      fvec[i] = y[i] - (x[0] + tmp1/(x[1]*tmp2 + x[2]*tmp3));
    }
  } else {
    /* compute Jacobian */
    for (i=0; i < 15; ++i) {
      tmp1 = i + 1;
      tmp2 = 15 - i;
#    ifdef TCHKDER_FIXED
      tmp3 = (i > 7) ? tmp2 : tmp1;
#    else
      /* error introduced into next statement for illustration. */
      /* corrected statement should read    tmp3 = (i > 7) ? tmp2 : tmp1 . */
      tmp3 = (i > 7) ? tmp2 : tmp2;
#    endif
      tmp4 = (x[1]*tmp2 + x[2]*tmp3); tmp4 = tmp4*tmp4;
      fjac[i + ldfjac*0] = -1.;
      fjac[i + ldfjac*1] = tmp1*tmp2/tmp4;
      fjac[i + ldfjac*2] = tmp1*tmp3/tmp4;
    }
#  ifdef BOX_CONSTRAINTS
    for (j = 0; j < 3; ++j) {
      for (i=0; i < 15; ++i) {
        fjac[i + ldfjac*j] *= jacfac[j];
      }
    }
#  endif
  }
  return 0;
}

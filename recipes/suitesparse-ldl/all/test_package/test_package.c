// https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/LDL/Demo/ldlsimple.c

//------------------------------------------------------------------------------
// LDL/Demo/ldlsimple.c: a simple LDL main program (int32_t version)
//------------------------------------------------------------------------------

// LDL, Copyright (c) 2005-2022 by Timothy A. Davis. All Rights Reserved.
// SPDX-License-Identifier: LGPL-2.1+

//------------------------------------------------------------------------------

/* LDLSIMPLE:  this is a very simple main program that illustrates the basic
 * usage of the LDL routines.  The output of this program is in ldlsimple.out.
 * This program factorizes the matrix
 *
 *    A =[ ...
 *    1.7     0     0     0     0     0     0     0   .13     0
 *      0    1.     0     0   .02     0     0     0     0   .01
 *      0     0   1.5     0     0     0     0     0     0     0
 *      0     0     0   1.1     0     0     0     0     0     0
 *      0   .02     0     0   2.6     0   .16   .09   .52   .53
 *      0     0     0     0     0   1.2     0     0     0     0
 *      0     0     0     0   .16     0   1.3     0     0   .56
 *      0     0     0     0   .09     0     0   1.6   .11     0
 *    .13     0     0     0   .52     0     0   .11   1.4     0
 *      0   .01     0     0   .53     0   .56     0     0   3.1 ] ;
 *
 * and then solves a system Ax=b whose true solution is
 * x = [.1 .2 .3 .4 .5 .6 .7 .8 .9 1]' ;
 *
 * Note that Li and Lx are statically allocated, with length 13.  This is just
 * enough to hold the factor L, but normally this size is not known until after
 * ldl_symbolic has analyzed the matrix.  The size of Li and Lx must be greater
 * than or equal to lnz = Lp [N], which is 13 for this matrix L.
 */

#include <stdio.h>
#include "ldl.h"
#define N 10	/* A is 10-by-10 */
#define ANZ 19	/* # of nonzeros on diagonal and upper triangular part of A */
#define LNZ 13	/* # of nonzeros below the diagonal of L */

int main (void)
{
    /* only the upper triangular part of A is required */
    int32_t Ap [N+1] = {0, 1, 2, 3, 4,   6, 7,   9,   11,      15,     ANZ},
           Ai [ANZ] = {0, 1, 2, 3, 1,4, 5, 4,6, 4,7, 0,4,7,8, 1,4,6,9 } ;
    double Ax [ANZ] = {1.7, 1., 1.5, 1.1, .02,2.6, 1.2, .16,1.3, .09,1.6,
		     .13,.52,.11,1.4, .01,.53,.56,3.1},
           b [N] = {.287, .22, .45, .44, 2.486, .72, 1.55, 1.424, 1.621, 3.759};
    double Lx [LNZ], D [N], Y [N] ;
    int Li [LNZ], Lp [N+1], Parent [N], Lnz [N], Flag [N], Pattern [N], d, i ;

    int version [3] ;
    SuiteSparse_version (version) ;
    printf ("LDL %d.%d.%d in SuiteSparse %d.%d.%d\n",
        LDL_MAIN_VERSION, LDL_SUB_VERSION, LDL_SUBSUB_VERSION,
        version [0], version [1], version [2]) ;

    /* factorize A into LDL' (P and Pinv not used) */
    ldl_symbolic (N, Ap, Ai, Lp, Parent, Lnz, Flag, NULL, NULL) ;
    printf ("Nonzeros in L, excluding diagonal: %d\n", Lp [N]) ;
    d = ldl_numeric (N, Ap, Ai, Ax, Lp, Parent, Lnz, Li, Lx, D, Y, Pattern,
	Flag, NULL, NULL) ;

    if (d == N)
    {
	/* solve Ax=b, overwriting b with the solution x */
	ldl_lsolve (N, b, Lp, Li, Lx) ;
	ldl_dsolve (N, b, D) ;
	ldl_ltsolve (N, b, Lp, Li, Lx) ;
	for (i = 0 ; i < N ; i++) printf ("x [%d] = %g\n", i, b [i]) ;
    }
    else
    {
	printf ("ldl_numeric failed, D (%d,%d) is zero\n", d, d) ;
    }
    return (0) ;
}

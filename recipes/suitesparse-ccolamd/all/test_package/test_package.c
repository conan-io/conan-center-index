// https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/CCOLAMD/Demo/ccolamd_l_example.c

//------------------------------------------------------------------------------
// CCOLAMD/Demo/ccolamd_l_example: simple example for CCOLAMD (int64_t)
//------------------------------------------------------------------------------

// CCOLAMD, Copyright (c) 2005-2022, Univ. of Florida, All Rights Reserved.
// Authors: Timothy A. Davis, Sivasankaran Rajamanickam, and Stefan Larimore.
// SPDX-License-Identifier: BSD-3-clause

//------------------------------------------------------------------------------

/*
 *  ccolamd example of use, to order the columns of a 5-by-4 matrix with
 *  11 nonzero entries in the following nonzero pattern, with default knobs
 *  and no ordering constraints.
 *
 *     x 0 x 0
 *     x 0 x x
 *     0 x x 0
 *     0 0 x x
 *     x x 0 0
 *
 *  csymamd example of use, to order the rows and columns of a 5-by-5
 *  matrix with 13 nonzero entries in the following nonzero pattern,
 *  with default knobs and no ordering constraints.
 *
 *     x x 0 0 0
 *     x x x x 0
 *     0 x x 0 0
 *     0 x 0 x x
 *     0 0 0 x x
 *
 *  (where x denotes a nonzero value).
 */

/* ========================================================================== */

#include <ccolamd.h>

#include <stdio.h>

#define A_NNZ 11
#define A_NROW 5
#define A_NCOL 4
#define ALEN 150    /* size max (2.2*nnz+17*ncol+7*nrow+6, 23*ncol+7*nrow+6) */

#define B_NNZ 4
#define B_N 5

int main (void)
{

    /* ====================================================================== */
    /* input matrix A definition */
    /* ====================================================================== */

    int64_t A [ALEN] = {

    	0, 1, 4,		/* row indices of nonzeros in column 0 */
	2, 4,			/* row indices of nonzeros in column 1 */
	0, 1, 2, 3,		/* row indices of nonzeros in column 2 */
	1, 3} ;			/* row indices of nonzeros in column 3 */

    int64_t p [ ] = {

    	0,			/* column 0 is in A [0..2] */
	3,			/* column 1 is in A [3..4] */
	5,			/* column 2 is in A [5..8] */
	9,			/* column 3 is in A [9..10] */
	A_NNZ} ;		/* number of nonzeros in A */

    /* ====================================================================== */
    /* input matrix B definition */
    /* ====================================================================== */

    int64_t B [ ] = {  /* Note: only strictly lower triangular part */
    				/* is included, since symamd ignores the */
				/* diagonal and upper triangular part of B. */

    	1,			/* row indices of nonzeros in column 0 */
    	2, 3,			/* row indices of nonzeros in column 1 */
    				/* row indices of nonzeros in column 2 (none) */
    	4			/* row indices of nonzeros in column 3 */
    	} ;			/* row indices of nonzeros in column 4 (none) */

    int64_t q [ ] = {

    	0,			/* column 0 is in B [0] */
	1,			/* column 1 is in B [1..2] */
	3,			/* column 2 is empty */
	3,			/* column 3 is in B [3] */
	4,			/* column 4 is empty */
	B_NNZ} ;		/* number of nonzeros in strictly lower B */

    /* ====================================================================== */
    /* other variable definitions */
    /* ====================================================================== */

    int64_t perm [B_N+1] ;	    /* note the size is N+1 */
    int64_t stats [CCOLAMD_STATS] ;  /* ccolamd/csymamd output stats */
    int64_t row, col, pp, length ;
    int ok ;

    //--------------------------------------------------------------------------
    // ccolamd version
    //--------------------------------------------------------------------------

    int version [3] ;
    ccolamd_version (version) ;
    printf ("CCOLAMD v%d.%d.%d\n", version [0], version [1], version [2]) ;
    if ((version [0] != CCOLAMD_MAIN_VERSION) ||
        (version [1] != CCOLAMD_SUB_VERSION) ||
        (version [2] != CCOLAMD_SUBSUB_VERSION))
    {
        fprintf (stderr, "version in header does not match library\n") ;
        abort ( ) ;
    }

    /* ====================================================================== */
    /* dump the input matrix A */
    /* ====================================================================== */

    printf ("ccolamd %d-by-%d input matrix:\n", A_NROW, A_NCOL) ;
    for (col = 0 ; col < A_NCOL ; col++)
    {
	length = p [col+1] - p [col] ;
    	printf ("Column %"PRId64", with %"PRId64" entries:\n", col, length) ;
	for (pp = p [col] ; pp < p [col+1] ; pp++)
	{
	    row = A [pp] ;
	    printf ("    row %"PRId64"\n", row) ;
	}
    }

    /* ====================================================================== */
    /* order the matrix.  Note that this destroys A and overwrites p */
    /* ====================================================================== */

    ok = ccolamd_l (A_NROW, A_NCOL, ALEN, A, p, (double *) NULL, stats, NULL) ;
    ccolamd_l_report (stats) ;

    if (!ok)
    {
	printf ("ccolamd error!\n") ;
	exit (1) ;
    }

    /* ====================================================================== */
    /* print the column ordering */
    /* ====================================================================== */

    printf ("ccolamd_l column ordering:\n") ;
    printf ("1st column: %"PRId64"\n", p [0]) ;
    printf ("2nd column: %"PRId64"\n", p [1]) ;
    printf ("3rd column: %"PRId64"\n", p [2]) ;
    printf ("4th column: %"PRId64"\n", p [3]) ;

    /* ====================================================================== */
    /* dump the strictly lower triangular part of symmetric input matrix B */
    /* ====================================================================== */

    printf ("\n\ncsymamd_l %d-by-%d input matrix:\n", B_N, B_N) ;
    printf ("Entries in strictly lower triangular part:\n") ;
    for (col = 0 ; col < B_N ; col++)
    {
	length = q [col+1] - q [col] ;
    	printf ("Column %"PRId64", with %"PRId64" entries:\n", col, length) ;
	for (pp = q [col] ; pp < q [col+1] ; pp++)
	{
	    row = B [pp] ;
	    printf ("    row %"PRId64"\n", row) ;
	}
    }

    /* ====================================================================== */
    /* order the matrix B.  Note that this does not modify B or q. */
    /* ====================================================================== */

    ok = csymamd_l (B_N, B, q, perm, (double *) NULL, stats, &calloc, &free,
	    NULL, -1) ;
    csymamd_l_report (stats) ;

    if (!ok)
    {
	printf ("csymamd error!\n") ;
	exit (1) ;
    }

    /* ====================================================================== */
    /* print the symmetric ordering */
    /* ====================================================================== */

    printf ("csymamd_l column ordering:\n") ;
    printf ("1st row/column: %"PRId64"\n", perm [0]) ;
    printf ("2nd row/column: %"PRId64"\n", perm [1]) ;
    printf ("3rd row/column: %"PRId64"\n", perm [2]) ;
    printf ("4th row/column: %"PRId64"\n", perm [3]) ;
    printf ("5th row/column: %"PRId64"\n", perm [4]) ;

    return (0) ;
}

/*
   LAPACKE Example : Calling DGELS using col-major layout
   =====================================================
   The program computes the solution to the system of linear
   equations with a square matrix A and multiple
   right-hand sides B, where A is the coefficient matrix
   and b is the right-hand side matrix:
   Description
   ===========
   In this example, we wish solve the least squares problem min_x || B - Ax ||
   for two right-hand sides using the LAPACK routine DGELS. For input we will
   use the 5-by-3 matrix
         ( 1  1  1 )
         ( 2  3  4 )
     A = ( 3  5  2 )
         ( 4  2  5 )
         ( 5  4  3 )
    and the 5-by-2 matrix
         ( -10 -3 )
         (  12 14 )
     B = (  14 12 )
         (  16 16 )
         (  18 16 )
    We will first store the input matrix as a static C two-dimensional array,
    which is stored in col-major layout, and let LAPACKE handle the work space
    array allocation. The LAPACK base name for this function is gels, and we
    will use double precision (d), so the LAPACKE function name is LAPACKE_dgels.
    lda=5 and ldb=5. The output for each right hand side is stored in b as
    consecutive vectors of length 3. The correct answer for this problem is
    the 3-by-2 matrix
         ( 2 1 )
         ( 1 1 )
         ( 1 2 )
    A complete C program for this example is given below. Note that when the arrays
     are passed to the LAPACK routine, they must be dereferenced, since LAPACK is
      expecting arrays of type double *, not double **.
   LAPACKE Interface
   =================
   LAPACKE_dgels (col-major, high-level) Example Program Results
  -- LAPACKE Example routine (version 3.7.0) --
  -- LAPACK is a software package provided by Univ. of Tennessee,    --
  -- Univ. of California Berkeley, Univ. of Colorado Denver and NAG Ltd..--
     December 2016
*/
/* Calling DGELS using col-major layout */

/* Includes */
#include <stdio.h>
#include <lapacke.h>

 int main() {
   double A[5][3] = {{1,2,3},{4,5,1},{3,5,2},{4,1,4},{2,5,3}};
   double b[5][2] = {{-10,12},{14,16},{18,-3},{14,12},{16,16}};

   const lapack_int m = 5;
   const lapack_int n = 3;
   const lapack_int lda = 5;
   const lapack_int ldb = 5;
   const lapack_int nrhs = 2;

   printf("LAPACKE_dgels (col-major, high-level) Example Program Results\n" );
   const lapack_int info = LAPACKE_dgels(LAPACK_COL_MAJOR,'N',m, n, nrhs, *A, lda, *b, ldb);
   printf( "Solution: %d %d %lf %d\n", n, nrhs, b[0][0], ldb);

   return info;
}

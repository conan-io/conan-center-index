#include <lapacke.h>

#include <stdio.h>

int main() {
    double a[4] = {3.0, 1.0, 1.0, 2.0};
    double b[2] = {9.0, 8.0};
    lapack_int n = 2;
    lapack_int nrhs = 1;
    lapack_int lda = 2;
    lapack_int ipiv[2];
    lapack_int ldb = 2;

    lapack_int info = LAPACKE_dgesv(LAPACK_ROW_MAJOR, n, nrhs, a, lda, ipiv, b, ldb);

    if(info != 0) {
        printf("LAPACKE_dgesv failed.\n");
        return 1;
    }

    printf("LAPACKE_dgesv() solution: \n");
    for(int i = 0; i < n; i++) {
        printf("%.1lf\n", b[i]);
    }

    return 0;
}

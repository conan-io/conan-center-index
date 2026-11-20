#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include <qrupdate.h>

#define TOL 1e-12

/* Cholesky factor R of A = I (upper triangular, column-major), updated with u so that
 * R1' * R1 = A + u * u' */
static int test_cholesky_update(void) {
    enum { N = 3 };
    qrupdate_fortran_double_t r[N * N] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
    qrupdate_fortran_double_t u[N] = {1, 2, 3};
    const qrupdate_fortran_double_t u0[N] = {1, 2, 3};
    qrupdate_fortran_double_t w[N] = {0};

    qrupdate_dch1up(N, r, N, u, w);

    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            /* (R1' * R1)(i, j) with R1 upper triangular */
            qrupdate_fortran_double_t sum = 0;
            for (int k = 0; k <= (i < j ? i : j); ++k) {
                sum += r[k + i * N] * r[k + j * N];
            }
            const qrupdate_fortran_double_t expected = (i == j ? 1.0 : 0.0) + u0[i] * u0[j];
            if (fabs(sum - expected) > TOL) {
                printf("dch1up mismatch at (%d, %d): %f != %f\n", i, j, sum, expected);
                return EXIT_FAILURE;
            }
        }
    }
    return EXIT_SUCCESS;
}

/* Build the QR factorization of A = [x1 x2] (3x2) by inserting its columns one by one
 * into the factorization of an empty matrix (Q = I): Q * R must give back A */
static int test_qr_column_insertion(void) {
    enum { M = 3 };
    qrupdate_fortran_double_t q[M * M] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
    qrupdate_fortran_double_t r[M * 2] = {0};
    qrupdate_fortran_double_t x1[M] = {1, 2, 3};
    qrupdate_fortran_double_t x2[M] = {4, -1, 2};
    const qrupdate_fortran_double_t a[M * 2] = {1, 2, 3, 4, -1, 2};
    qrupdate_fortran_double_t w[2 * M] = {0};

    qrupdate_dqrinc(M, 0, M, q, M, r, M, 1, x1, w);
    qrupdate_dqrinc(M, 1, M, q, M, r, M, 2, x2, w);

    for (int i = 0; i < M; ++i) {
        for (int j = 0; j < 2; ++j) {
            qrupdate_fortran_double_t sum = 0;
            for (int k = 0; k < M; ++k) {
                sum += q[i + k * M] * r[k + j * M];
            }
            if (fabs(sum - a[i + j * M]) > TOL) {
                printf("dqrinc mismatch at (%d, %d): %f != %f\n", i, j, sum, a[i + j * M]);
                return EXIT_FAILURE;
            }
        }
    }
    return EXIT_SUCCESS;
}

int main(void) {
    if (test_cholesky_update() != EXIT_SUCCESS || test_qr_column_insertion() != EXIT_SUCCESS) {
        return EXIT_FAILURE;
    }
    printf("qrupdate %s: dch1up and dqrinc OK\n", QRUPDATE_VERSION);
    return EXIT_SUCCESS;
}

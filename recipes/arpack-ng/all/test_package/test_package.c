#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include <arpack.h>

/* Largest eigenvalues of A = diag(1, 2, ..., N): N, N-1, ... */
#define N 100
#define NEV 4
#define NCV 20

int main(void) {
    a_int ido = 0, info = 0, n = N, nev = NEV, ncv = NCV, ldv = N, lworkl = NCV * (NCV + 8);
    a_int iparam[11] = {0}, ipntr[11] = {0}, select[NCV] = {0};
    double tol = 0.0, sigma = 0.0;
    double resid[N], v[N * NCV], workd[3 * N], workl[NCV * (NCV + 8)], d[NEV + 1];

    iparam[0] = 1;   /* exact shifts */
    iparam[2] = 300; /* max iterations */
    iparam[6] = 1;   /* mode 1: A x = lambda x */

    do {
        dsaupd_c(&ido, "I", n, "LA", nev, tol, resid, ncv, v, ldv, iparam, ipntr, workd, workl, lworkl, &info);
        if (ido == -1 || ido == 1) {
            for (int i = 0; i < N; ++i) {
                workd[ipntr[1] - 1 + i] = (i + 1) * workd[ipntr[0] - 1 + i];
            }
        }
    } while (ido == -1 || ido == 1);

    if (info < 0) {
        printf("dsaupd failed: info = %d\n", (int)info);
        return EXIT_FAILURE;
    }

    dseupd_c(1, "A", select, d, v, ldv, sigma, "I", n, "LA", nev, tol, resid, ncv, v, ldv, iparam, ipntr, workd, workl, lworkl, &info);
    if (info != 0) {
        printf("dseupd failed: info = %d\n", (int)info);
        return EXIT_FAILURE;
    }

    /* Eigenvalues are returned in ascending order */
    for (int i = 0; i < NEV; ++i) {
        printf("lambda[%d] = %f\n", i, d[i]);
        if (fabs(d[i] - (N - NEV + 1 + i)) > 1e-6) {
            return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}

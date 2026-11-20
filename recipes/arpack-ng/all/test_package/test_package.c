#include <stdio.h>
#include <stdlib.h>

#include <arpack.h>

int main(void) {
    a_int ido = 0, info = 0;
    a_int iparam[11] = {0}, ipntr[11] = {0};
    double resid[1], v[1], workd[3], workl[20];

    iparam[2] = 1; /* max iterations > 0 */
    iparam[6] = 1; /* mode 1: standard eigenproblem */

    /* n = 0 is invalid; nev = 1, ncv = 2, lworkl = ncv^2 + 8*ncv = 20 */
    dsaupd_c(&ido, "I", 0, "LA", 1, 0.0, resid, 2, v, 1, iparam, ipntr, workd, workl, 20, &info);

    printf("dsaupd_c returned info = %d\n", (int)info);
    return info == -1 ? EXIT_SUCCESS : EXIT_FAILURE;
}

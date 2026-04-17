#include <lapacke.h>

int main(void) {
    double a[4] = {1.0, 2.0, 3.0, 4.0};
    double wr[2] = {0.0, 0.0};
    double wi[2] = {0.0, 0.0};
    return LAPACKE_dgeev(LAPACK_ROW_MAJOR, 'N', 'N', 2, a, 2, wr, wi, 0, 1, 0, 1);
}

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fft/fft.h>
#include <fft/fft2.h>

#define N 2

int main()
{
    double A1[N];
    double A2[N];
    double * A[N] = {A1, A2};
    double B[N];
    int ip[N * 2];
    
    memset(A1, 0, sizeof(double) * N);
    memset(A2, 0, sizeof(double) * N);
    memset(B, 0, sizeof(double) * N);
    memset(ip, 0, sizeof(int) * N * 2);

    cdft2d(N, N, 1, A, NULL, ip, B);

    return EXIT_SUCCESS;
}

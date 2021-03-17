/* test of fftsg3d.c */

#include <math.h>
#include <stdio.h>
#include <fft/alloc.h>
#include <fft/fft3.h>
#define MAX(x,y) ((x) > (y) ? (x) : (y))

/* random number generator, 0 <= RND < 1 */
#define RND(p) ((*(p) = (*(p) * 7141 + 54773) % 259200) * (1.0 / 259200))


int main()
{
    void putdata3d(int n1, int n2, int n3, double ***a);
    double errorcheck3d(int n1, int n2, int n3, double scale, double ***a);
    int *ip, n1, n2, n3, n, nt, i, j;
    double ***a, *w, err;

    printf("data length n1=? (n1 = power of 2) \n");
    scanf("%d", &n1);
    printf("data length n2=? (n2 = power of 2) \n");
    scanf("%d", &n2);
    printf("data length n3=? (n3 = power of 2) \n");
    scanf("%d", &n3);

    a = alloc_3d_double(n1, n2, n3);
    nt = MAX(n1, n2);
    n = MAX(nt, n3 / 2);
    ip = alloc_1d_int(2 + (int) sqrt(n + 0.5));
    n = MAX(nt, n3) * 3 / 2;
    w = alloc_1d_double(n);
    ip[0] = 0;

    /* check of CDFT */
    putdata3d(n1, n2, n3, a);
    cdft3d(n1, n2, n3, 1, a, NULL, ip, w);
    cdft3d(n1, n2, n3, -1, a, NULL, ip, w);
    err = errorcheck3d(n1, n2, n3, 2.0 / n1 / n2 / n3, a);
    printf("cdft3d err= %g \n", err);

    /* check of RDFT */
    putdata3d(n1, n2, n3, a);
    rdft3d(n1, n2, n3, 1, a, NULL, ip, w);
    rdft3d(n1, n2, n3, -1, a, NULL, ip, w);
    err = errorcheck3d(n1, n2, n3, 2.0 / n1 / n2 / n3, a);
    printf("rdft3d err= %g \n", err);

    /* check of DDCT */
    putdata3d(n1, n2, n3, a);
    ddct3d(n1, n2, n3, 1, a, NULL, ip, w);
    ddct3d(n1, n2, n3, -1, a, NULL, ip, w);
    for (i = 0; i <= n1 - 1; i++) {
        for (j = 0; j <= n2 - 1; j++) {
            a[i][j][0] *= 0.5;
        }
        for (j = 0; j <= n3 - 1; j++) {
            a[i][0][j] *= 0.5;
        }
    }
    for (i = 0; i <= n2 - 1; i++) {
        for (j = 0; j <= n3 - 1; j++) {
            a[0][i][j] *= 0.5;
        }
    }
    err = errorcheck3d(n1, n2, n3, 8.0 / n1 / n2 / n3, a);
    printf("ddct3d err= %g \n", err);

    /* check of DDST */
    putdata3d(n1, n2, n3, a);
    ddst3d(n1, n2, n3, 1, a, NULL, ip, w);
    ddst3d(n1, n2, n3, -1, a, NULL, ip, w);
    for (i = 0; i <= n1 - 1; i++) {
        for (j = 0; j <= n2 - 1; j++) {
            a[i][j][0] *= 0.5;
        }
        for (j = 0; j <= n3 - 1; j++) {
            a[i][0][j] *= 0.5;
        }
    }
    for (i = 0; i <= n2 - 1; i++) {
        for (j = 0; j <= n3 - 1; j++) {
            a[0][i][j] *= 0.5;
        }
    }
    err = errorcheck3d(n1, n2, n3, 8.0 / n1 / n2 / n3, a);
    printf("ddst3d err= %g \n", err);

    free_1d_double(w);
    free_1d_int(ip);
    free_3d_double(a);
    return 0;
}


void putdata3d(int n1, int n2, int n3, double ***a)
{
    int j1, j2, j3, seed = 0;

    for (j1 = 0; j1 <= n1 - 1; j1++) {
        for (j2 = 0; j2 <= n2 - 1; j2++) {
            for (j3 = 0; j3 <= n3 - 1; j3++) {
                a[j1][j2][j3] = RND(&seed);
            }
        }
    }
}


double errorcheck3d(int n1, int n2, int n3, double scale, double ***a)
{
    int j1, j2, j3, seed = 0;
    double err = 0, e;

    for (j1 = 0; j1 <= n1 - 1; j1++) {
        for (j2 = 0; j2 <= n2 - 1; j2++) {
            for (j3 = 0; j3 <= n3 - 1; j3++) {
                e = RND(&seed) - a[j1][j2][j3] * scale;
                err = MAX(err, fabs(e));
            }
        }
    }
    return err;
}


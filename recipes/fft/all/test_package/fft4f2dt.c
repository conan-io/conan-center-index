/* test of fft4f2d.c */

#include <math.h>
#include <stdio.h>
#include <fft/alloc.h>
#include <fft/fft.h>
#include <fft/fft2.h>
#define MAX(x,y) ((x) > (y) ? (x) : (y))

/* random number generator, 0 <= RND < 1 */
#define RND(p) ((*(p) = (*(p) * 7141 + 54773) % 259200) * (1.0 / 259200))


int main()
{
    void putdata2d(int n1, int n2, double **a);
    double errorcheck2d(int n1, int n2, double scale, double **a);
    int *ip, n1, n2, n, i;
    double **a, **t, *w, err;

    printf("data length n1=? (n1 = power of 2) \n");
    scanf("%d", &n1);
    printf("data length n2=? (n2 = power of 2) \n");
    scanf("%d", &n2);

    a = alloc_2d_double(n1, n2);
    t = alloc_2d_double(n1, n2);
    n = MAX(n1, n2 / 2);
    ip = alloc_1d_int(2 + (int) sqrt(n + 0.5));
    n = MAX(n1 / 2, n2 / 4) + MAX(n1, n2);
    w = alloc_1d_double(n);
    ip[0] = 0;

    /* check of CDFT */
    putdata2d(n1, n2, a);
    cdft2d(n1, n2, 1, a, ip, w);
    cdft2d(n1, n2, -1, a, ip, w);
    err = errorcheck2d(n1, n2, 2.0 / n1 / n2, a);
    printf("cdft2d err= %g \n", err);

    /* check of RDFT */
    putdata2d(n1, n2, a);
    rdft2d(n1, n2, 1, a, ip, w);
    rdft2d(n1, n2, -1, a, ip, w);
    err = errorcheck2d(n1, n2, 2.0 / n1 / n2, a);
    printf("rdft2d err= %g \n", err);

    /* check of DDCT */
    putdata2d(n1, n2, a);
    ddct2d(n1, n2, 1, a, t, ip, w);
    ddct2d(n1, n2, -1, a, t, ip, w);
    for (i = 0; i <= n1 - 1; i++) {
        a[i][0] *= 0.5;
    }
    for (i = 0; i <= n2 - 1; i++) {
        a[0][i] *= 0.5;
    }
    err = errorcheck2d(n1, n2, 4.0 / n1 / n2, a);
    printf("ddct2d err= %g \n", err);

    /* check of DDST */
    putdata2d(n1, n2, a);
    ddst2d(n1, n2, 1, a, t, ip, w);
    ddst2d(n1, n2, -1, a, t, ip, w);
    for (i = 0; i <= n1 - 1; i++) {
        a[i][0] *= 0.5;
    }
    for (i = 0; i <= n2 - 1; i++) {
        a[0][i] *= 0.5;
    }
    err = errorcheck2d(n1, n2, 4.0 / n1 / n2, a);
    printf("ddst2d err= %g \n", err);

    free_1d_double(w);
    free_1d_int(ip);
    free_2d_double(t);
    free_2d_double(a);
    return 0;
}


void putdata2d(int n1, int n2, double **a)
{
    int j1, j2, seed = 0;

    for (j1 = 0; j1 <= n1 - 1; j1++) {
        for (j2 = 0; j2 <= n2 - 1; j2++) {
            a[j1][j2] = RND(&seed);
        }
    }
}


double errorcheck2d(int n1, int n2, double scale, double **a)
{
    int j1, j2, seed = 0;
    double err = 0, e;

    for (j1 = 0; j1 <= n1 - 1; j1++) {
        for (j2 = 0; j2 <= n2 - 1; j2++) {
            e = RND(&seed) - a[j1][j2] * scale;
            err = MAX(err, fabs(e));
        }
    }
    return err;
}


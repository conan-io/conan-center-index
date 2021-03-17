/* test of shrtdct.c */

#include <math.h>
#include <stdio.h>
#include <fft/dct.h>
#define MAX(x,y) ((x) > (y) ? (x) : (y))

/* random number generator, 0 <= RND < 1 */
#define RND(p) ((*(p) = (*(p) * 7141 + 54773) % 259200) * (1.0 / 259200))

#define NMAX 16

int main()
{
    void putdata2d(int n1, int n2, double **a);
    double errorcheck2d(int n1, int n2, double scale, double **a);
    double err;
    
    int i;
    double aarr[NMAX][NMAX], *a[NMAX], barr[NMAX][NMAX], *b[NMAX];
    for (i = 0; i < NMAX; i++) a[i] = aarr[i];
    for (i = 0; i < NMAX; i++) b[i] = barr[i];

    /* check of 8x8 DCT */
    putdata2d(8, 8, a);
    ddct8x8s(-1, a);
    ddct8x8s(1, a);
    err = errorcheck2d(8, 8, 1.0, a);
    printf("ddct8x8s   err= %g\n", err);

    /* check of 16x16 DCT */
    putdata2d(16, 16, a);
    ddct16x16s(-1, a);
    ddct16x16s(1, a);
    err = errorcheck2d(16, 16, 1.0, a);
    printf("ddct16x16s err= %g\n", err);

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


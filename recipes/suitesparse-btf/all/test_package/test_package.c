#include <btf.h>

#define N 10
#define NZ 10

int main()
{
    int n, Ap [N+1], Ai [NZ], P [N], Q [N], R [N+1], nfound, Work [5*N], ncomp ;
    double maxwork, work ;
    ncomp = btf_order (N, Ap, Ai, maxwork, &work, P, Q, R, &nfound, Work) ;
}

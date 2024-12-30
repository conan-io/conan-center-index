#include "IpLinearSolvers.h"

#include <cstdio>
#include <cstdlib>

int main()
{
    IpoptLinearSolver solvers = IpoptGetAvailableLinearSolvers(false);

    puts("Available linear solvers:");

    if (solvers & IPOPTLINEARSOLVER_MA27) {
        puts("- ma27");
    }
    if (solvers & IPOPTLINEARSOLVER_MA57) {
        puts("- ma57");
    }
    if (solvers & IPOPTLINEARSOLVER_MA77) {
        puts("- ma77");
    }
    if (solvers & IPOPTLINEARSOLVER_MA86) {
        puts("- ma86");
    }
    if (solvers & IPOPTLINEARSOLVER_MA97) {
        puts("- ma97");
    }
    if (solvers & IPOPTLINEARSOLVER_MC19) {
        puts("- mc19");
    }
    if (solvers & IPOPTLINEARSOLVER_MUMPS) {
        puts("- mumps");
    }
    if (solvers & IPOPTLINEARSOLVER_PARDISO) {
        puts("- pardiso");
    }
    if (solvers & IPOPTLINEARSOLVER_PARDISOMKL) {
        puts("- pardisomkl");
    }
    if (solvers & IPOPTLINEARSOLVER_SPRAL) {
        puts("- spral");
    }
    if (solvers & IPOPTLINEARSOLVER_WSMP) {
        puts("- wsmp");
    }
    return 0;
}

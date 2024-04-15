// https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/ParU/Demo/paru_simplec.c

//  =========================================================================  /
// =======================  paru_simplec.c  =================================  /
// ==========================================================================  /

// ParU, Copyright (c) 2022, Mohsen Aznaveh and Timothy A. Davis,
// All Rights Reserved.
// SPDX-License-Identifier: GNU GPL 3.0

/*
 * @brief   a simple test to show how to use ParU with C interface
 * @author Aznaveh
 * */

#include <ParU_C.h>

#include <stdint.h>
#include <math.h>

int main(int argc, char **argv)
{
    cholmod_common Common, *cc;
    cholmod_sparse *A;
    ParU_C_Symbolic *Sym;
    //~~~~~~~~~Reading the input matrix and test if the format is OK~~~~~~~~~~~~
    // start CHOLMOD
    cc = &Common;
    int mtype;
    cholmod_l_start(cc);
    // A = mread (stdin) ; read in the sparse matrix A
    A = (cholmod_sparse *)cholmod_l_read_matrix(stdin, 1, &mtype, cc);
    //~~~~~~~~~~~~~~~~~~~Starting computation~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    printf("================= ParU, a simple demo, using C interface : ====\n");
    ParU_C_Control Control;
    ParU_C_Init_Control(&Control);
    ParU_Ret info;
    info = ParU_C_Analyze(A, &Sym, &Control);
    printf("Input matrix is %" PRId64 "x%" PRId64 " nnz = %" PRId64 " \n", Sym->m, Sym->n, Sym->anz);
    ParU_C_Numeric *Num;
    info = ParU_C_Factorize(A, Sym, &Num, &Control);

    if (info != PARU_SUCCESS)
    {
        printf("ParU: factorization was NOT successful.");
        if (info == PARU_OUT_OF_MEMORY) printf("\nOut of memory\n");
        if (info == PARU_INVALID) printf("\nInvalid!\n");
        if (info == PARU_SINGULAR) printf("\nSingular!\n");
    }
    else
    {
        printf("ParU: factorization was successful.\n");
    }

    //~~~~~~~~~~~~~~~~~~~ Computing Ax = b ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#if 1
    if (info == PARU_SUCCESS)
    {
        int64_t m = Sym->m;
        double *b = (double *)malloc(m * sizeof(double));
        double *xx = (double *)malloc(m * sizeof(double));
        for (int64_t i = 0; i < m; ++i) b[i] = i + 1;
        info = ParU_C_Solve_Axb(Sym, Num, b, xx, &Control);
        double resid, anorm, xnorm;
        info =
            ParU_C_Residual_bAx(A, xx, b, m, &resid, &anorm, &xnorm, &Control);
        double rresid = (anorm == 0 || xnorm == 0 ) ? 0 : (resid/(anorm*xnorm));
        printf( "Relative residual is |%.2e|, anorm is %.2e, xnorm is %.2e "
            " and rcond is %.2e.\n", rresid, anorm, xnorm, Num->rcond);
        free(b);
        free(xx);
    }
#endif  // testing the results
    //~~~~~~~~~~~~~~~~~~~End computation~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ParU_C_Freenum(&Num, &Control);
    ParU_C_Freesym(&Sym, &Control);

    cholmod_l_free_sparse(&A, cc);
    cholmod_l_finish(cc);
}

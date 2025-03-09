#include <ParU.h>

#include <stdio.h>

int main(int argc, char **argv)
{
    cholmod_common Common, *cc = NULL ;
    cholmod_sparse *A = NULL ;
    ParU_C_Symbolic Sym = NULL ;
    ParU_C_Control Control = NULL ;

    cc = &Common;
    int mtype;
    cholmod_l_start(cc);

    // read in the sparse matrix A from stdin
    A = (cholmod_sparse *)cholmod_l_read_matrix(stdin, 1, &mtype, cc);
    if (A == NULL)
    {
        printf("unable to read matrix\n") ;
        return 1;
    }

    ParU_C_Analyze(A, &Sym, Control);
}

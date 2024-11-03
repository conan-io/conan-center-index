#include <cs.h>

int main()
{
    int version[3];
    cxsparse_version(version);
    printf("CXSparse v%d.%d.%d\n", version [0], version [1], version [2]);

#ifdef NCOMPLEX
    printf("Complex-valued matrices are not supported.\n");
#else
    printf("Complex-valued matrices are supported.\n");
#endif

}

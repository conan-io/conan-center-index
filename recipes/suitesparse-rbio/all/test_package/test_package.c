#include <RBio.h>

#include <stdio.h>


int main (int argc, char **argv)
{
    printf ("RBio version %d.%d.%d, date: %s\n",
        RBIO_MAIN_VERSION, RBIO_SUB_VERSION, RBIO_SUBSUB_VERSION, RBIO_DATE) ;
    int version [3] ;
    RBio_version (version) ;
    if ((version [0] != RBIO_MAIN_VERSION) ||
        (version [1] != RBIO_SUB_VERSION) ||
        (version [2] != RBIO_SUBSUB_VERSION))
    {
        fprintf (stderr, "version in header does not match library\n") ;
        abort ( ) ;
    }

    SuiteSparse_start ( ) ;
    SuiteSparse_finish ( ) ;
    return (0) ;
}

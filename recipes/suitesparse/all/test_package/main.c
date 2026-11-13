#include <stdio.h>

#include "suitesparse_config.h"
#include "amd.h"
#include "btf.h"
#include "camd.h"
#include "ccolamd.h"
#include "colamd.h"
#include "cs.h"
#include "ldl.h"
#include "klu.h"
#include "umfpack.h"
#include "cholmod.h"
#include "RBio.h"
#include "SPEX.h"
#include "GraphBLAS.h"
#include "LAGraph.h"

/* Force the linker to resolve one symbol per library for which there is no
 * cheap, side-effect-free call. The volatile function pointer prevents the
 * compiler from optimizing the reference away, which matters for static
 * libraries where unused archives are not searched at all. */
#define LINK_REF(fn) \
    do { void (* volatile keep)(void) = (void (*)(void))(fn); (void)keep; } while (0)

int main(void)
{
    int version[3] = {0, 0, 0};

    SuiteSparse_version(version);
    printf("SuiteSparse_config: %d.%d.%d\n", version[0], version[1], version[2]);

    /* ordering libraries: link-check only */
    LINK_REF(amd_l_order);
    LINK_REF(camd_order);
    LINK_REF(ccolamd);
    LINK_REF(colamd);
    LINK_REF(klu_l_free_symbolic);
    LINK_REF(umfpack_di_free_numeric);
    LINK_REF(SPEX_matrix_allocate);
    printf("AMD/CAMD/COLAMD/CCOLAMD/KLU/UMFPACK/SPEX: linked\n");

    btf_version(version);
    printf("BTF: %d.%d.%d\n", version[0], version[1], version[2]);

    cxsparse_version(version);
    printf("CXSparse: %d.%d.%d\n", version[0], version[1], version[2]);

    ldl_version(version);
    printf("LDL: %d.%d.%d\n", version[0], version[1], version[2]);

    RBio_version(version);
    printf("RBio: %d.%d.%d\n", version[0], version[1], version[2]);

    /* CHOLMOD: real start/finish cycle */
    cholmod_common common;
    if (!cholmod_start(&common)) {
        fprintf(stderr, "cholmod_start failed\n");
        return 1;
    }
    printf("CHOLMOD: %d.%d.%d\n", CHOLMOD_MAIN_VERSION, CHOLMOD_SUB_VERSION,
           CHOLMOD_SUBSUB_VERSION);
    cholmod_finish(&common);

    /* GraphBLAS: real init/finalize cycle */
    if (GrB_init(GrB_NONBLOCKING) != GrB_SUCCESS) {
        fprintf(stderr, "GrB_init failed\n");
        return 1;
    }
    printf("GraphBLAS: linked and initialized\n");
    GrB_finalize();

    /* LAGraph: real init/finalize cycle (requires GraphBLAS) */
    char message[256] = "";
    if (LAGraph_Init(message) != GrB_SUCCESS) {
        fprintf(stderr, "LAGraph_Init failed: %s\n", message);
        return 1;
    }
    printf("LAGraph: linked and initialized\n");
    LAGraph_Finalize(message);

    return 0;
}

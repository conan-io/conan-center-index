#include <cstdio>

#include "SuiteSparseQR.hpp"
#include "ParU.h"
#include "Mongoose.hpp"
#include "SPEX.h"
#include "GraphBLAS.h"

int main()
{
    int version[3] = {0, 0, 0};

    SuiteSparseQR_version(version);
    std::printf("SPQR: %d.%d.%d\n", version[0], version[1], version[2]);

    char date[128] = {0};
    if (ParU_Version(version, date) != PARU_SUCCESS) {
        std::fprintf(stderr, "ParU_Version failed\n");
        return 1;
    }
    std::printf("ParU: %d.%d.%d (%s)\n", version[0], version[1], version[2], date);

    std::printf("Mongoose: %d.%d.%d\n", Mongoose::major_version(),
                Mongoose::minor_version(), Mongoose::patch_version());

    // SPEX_initialize() sets the GMP/MPFR memory functions, so it needs both libraries to link
    if (SPEX_initialize() != SPEX_OK) {
        std::fprintf(stderr, "SPEX_initialize failed\n");
        return 1;
    }
    SPEX_finalize();
    std::printf("SPEX: initialized\n");

    if (GrB_init(GrB_NONBLOCKING) != GrB_SUCCESS) {
        std::fprintf(stderr, "GrB_init failed\n");
        return 1;
    }
    GrB_finalize();
    std::printf("GraphBLAS: initialized\n");

    return 0;
}

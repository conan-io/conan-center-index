#include <cstdio>

#include "SuiteSparseQR.hpp"
#include "ParU.h"
#include "Mongoose.hpp"

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

    return 0;
}

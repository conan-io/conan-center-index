#include <cgnslib.h>

#include <cstdio>

int main() {
    int indexFile;
    int indexBase;

    cg_open("test.cgns", CG_MODE_WRITE, &indexFile);

    cg_base_write(indexFile, "Base2D", 2, 3, &indexBase);

    // test a global variable
    printf("MassUnits: ");
    for (unsigned i = 0; i < NofValidMassUnits; ++i) {
        printf("%s ", MassUnitsName[i]);
    }
    printf("\n");

    return 0;
}

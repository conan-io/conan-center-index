#include <cgnslib.h>

int main() {
    int indexFile;
    int indexBase;

    cg_open("test.cgns", CG_MODE_WRITE, &indexFile);

    cg_base_write(indexFile, "Base2D", 2, 3, &indexBase);

    return 0;
}

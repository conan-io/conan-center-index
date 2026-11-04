#include <libmeshb7.h>

int main() {
   int ver, dim;
   int64_t LibIdx = GmfOpenMesh("/dev/null", GmfRead, &ver, &dim);
   return 0;
}

#include <stdio.h>

#include <vl/generic.h>
#include <vl/sift.h>

int main() {
    VL_PRINT("Hello World! This is VLFeat.\n");

    VlSiftFilt *sift = vl_sift_new(256, 256, -1, 3, 0);

    if (!sift) {
        printf("Failed to initialize SIFT descriptor.\n");
        return 1;
    }

    vl_sift_delete(sift);

    return 0;
}

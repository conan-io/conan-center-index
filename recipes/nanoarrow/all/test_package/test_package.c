#include <nanoarrow/nanoarrow.h>
#include <stdio.h>

int main() {
    struct ArrowSchema schema;
    ArrowSchemaInit(&schema);
    int result = ArrowSchemaSetType(&schema, NANOARROW_TYPE_INT32);
    if (result != NANOARROW_OK) {
        fprintf(stderr, "ArrowSchemaSetType failed\n");
        return 1;
    }
    ArrowSchemaRelease(&schema);
    printf("nanoarrow test passed\n");
    return 0;
}


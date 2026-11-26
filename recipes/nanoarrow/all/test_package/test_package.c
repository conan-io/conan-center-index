#include <nanoarrow/nanoarrow.h>
#include <stdio.h>

#ifdef NANOARROW_TEST_WITH_IPC
#include <nanoarrow/nanoarrow_ipc.h>
#endif

int main() {
    struct ArrowSchema schema;
    ArrowSchemaInit(&schema);
    int result = ArrowSchemaSetType(&schema, NANOARROW_TYPE_INT32);
    if (result != NANOARROW_OK) {
        fprintf(stderr, "ArrowSchemaSetType failed\n");
        return 1;
    }
    ArrowSchemaRelease(&schema);

#ifdef NANOARROW_TEST_WITH_IPC
    struct ArrowIpcDecoder decoder;
    ArrowIpcDecoderInit(&decoder);
    printf("nanoarrow ipc test passed\n");
#endif

    printf("nanoarrow test passed\n");
    return 0;
}

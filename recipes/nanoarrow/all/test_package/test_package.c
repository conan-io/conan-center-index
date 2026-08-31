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
    /* Verifying a (bogus) header goes through the vendored flatcc runtime, so this
     * only links when nanoarrow::nanoarrow_ipc carries libflatccrt. */
    struct ArrowIpcDecoder decoder;
    if (ArrowIpcDecoderInit(&decoder) != NANOARROW_OK) {
        fprintf(stderr, "ArrowIpcDecoderInit failed\n");
        return 1;
    }
    unsigned char bogus[8] = {0xff, 0xff, 0xff, 0xff, 0x00, 0x00, 0x00, 0x00};
    struct ArrowBufferView view;
    view.data.as_uint8 = bogus;
    view.size_bytes = (int64_t)sizeof(bogus);
    struct ArrowError error;
    (void)ArrowIpcDecoderVerifyHeader(&decoder, view, &error);
    ArrowIpcDecoderReset(&decoder);
    printf("nanoarrow ipc test passed\n");
#endif

    printf("nanoarrow test passed\n");
    return 0;
}

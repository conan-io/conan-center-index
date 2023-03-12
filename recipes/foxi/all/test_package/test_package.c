#include <foxi/onnxifi_loader.h>

#include <stdio.h>
#include <dlfcn.h>

#ifndef ONNXIFI_PATH
#define ONNXIFI_PATH NULL // let the library decide
#endif

int main() {
#ifdef ONNXIFI_REQUIRES_PTHREAD_SYMBOLS
    // We need to load pthreads before loading onnxifi to resolve all missing symbols
    void* handlePthread = dlopen("libpthread.so", RTLD_GLOBAL | RTLD_LAZY);
    if(!handlePthread ){
        fprintf(stderr, "dlopen failed: %s\n", dlerror());
        return 1;
    }
#endif

    struct onnxifi_library onnx;
    int ret = onnxifi_load(ONNXIFI_LOADER_FLAG_VERSION_1_0, ONNXIFI_PATH, &onnx);
    if (!ret) {
        printf("Cannot load onnxifi lib\n");
        return -1;
    }
    onnxifi_unload(&onnx);
    printf("SUCCESS! onnxifi has been loaded & unloaded successfully.\n");
    return 0;
}

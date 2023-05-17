#include <foxi/onnxifi_loader.h>

#include <stdio.h>

int main() {
    struct onnxifi_library onnx;
    int ret = onnxifi_load(ONNXIFI_LOADER_FLAG_VERSION_1_0, NULL, &onnx);
    if (!ret) {
        printf("Cannot load onnxifi lib\n");
        return 0;
    }
    onnxifi_unload(&onnx);
    return 0;
}

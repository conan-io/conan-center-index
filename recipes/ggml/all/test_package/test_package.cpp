#include <iostream>

#include "ggml.h"

int main() {
    ggml_init_params params{};
    params.mem_size = 1024 * 1024;
    params.mem_buffer = nullptr;
    params.no_alloc = true;

    ggml_context* ctx = ggml_init(params);
    if (!ctx) {
        return 1;
    }

    ggml_tensor* tensor = ggml_new_tensor_1d(ctx, GGML_TYPE_F32, 4);
    std::cout << "elements=" << ggml_nelements(tensor) << std::endl;

    ggml_free(ctx);
    return 0;
}

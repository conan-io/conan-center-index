#include "wasmer.h"

#include <stdio.h>
#include <stdlib.h>

int main() {
    wasm_engine_t* engine = wasm_engine_new();

    if (engine == NULL) {
        fprintf(stderr, "wasm_engine_new failed\n");
        return EXIT_FAILURE;
    }
    wasm_engine_delete(engine);
    return EXIT_SUCCESS;
}

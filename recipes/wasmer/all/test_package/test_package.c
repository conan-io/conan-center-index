#include "wasmer.h"

#include "assert.h"

int main() {
    wasm_engine_t* engine = wasm_engine_new();

    assert(engine);

    wasm_engine_delete(engine);

    return EXIT_SUCCESS;
}

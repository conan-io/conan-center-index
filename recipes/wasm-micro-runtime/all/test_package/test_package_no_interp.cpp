#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "wasm_c_api.h"

#define own

// A function to be called from Wasm code.
own wasm_trap_t* hello_callback(
  const wasm_val_vec_t* args, wasm_val_vec_t* results
) {
  printf("Calling back...\n");
  printf("> Hello World!\n");
  return NULL;
}

int main(int argc, const char* argv[]) {
  // Initialize.
  printf("Initializing...\n");
  wasm_engine_t* engine = wasm_engine_new();
  wasm_store_t* store = wasm_store_new(engine);

  // Load binary.
  printf("Loading binary...\n");
  FILE* file = fopen(argv[1], "rb");
  if (!file) {
    printf("> Error loading module!\n");
    return 1;
  }

  long file_size = 10240;

  wasm_byte_vec_t binary;
  wasm_byte_vec_new_uninitialized(&binary, file_size);

  // Compile.
  printf("Compiling module...\n");
  own wasm_module_t* module = wasm_module_new(store, &binary);

  wasm_byte_vec_delete(&binary);

  // Create external print functions.
  printf("Creating callback...\n");
  own wasm_functype_t* hello_type = wasm_functype_new_0_0();
  own wasm_func_t* hello_func =
    wasm_func_new(store, hello_type, hello_callback);

  wasm_functype_delete(hello_type);

  wasm_func_delete(hello_func);

  wasm_module_delete(module);

  // Shut down.
  printf("Shutting down...\n");
  wasm_store_delete(store);
  wasm_engine_delete(engine);

  // All done.
  printf("Done.\n");
  return 0;
}

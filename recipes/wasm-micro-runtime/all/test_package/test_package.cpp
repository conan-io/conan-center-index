#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>

#include "wasm_c_api.h"

#define own

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

  int ret = fseek(file, 0L, SEEK_END);
  if (ret == -1) {
    printf("> Error loading module!\n");
    fclose(file);
    return 1;
  }

  long file_size = ftell(file);
  if (file_size == -1) {
    printf("> Error loading module!\n");
    fclose(file);
    return 1;
  }

  ret = fseek(file, 0L, SEEK_SET);
  if (ret == -1) {
    printf("> Error loading module!\n");
    fclose(file);
    return 1;
  }

  wasm_byte_vec_t binary;
  wasm_byte_vec_new_uninitialized(&binary, file_size);
  if (fread(binary.data, file_size, 1, file) != 1) {
    printf("> Error loading module!\n");
    fclose(file);
    return 1;
  }
  fclose(file);

  // Compile.
  printf("Compiling module...\n");
  own wasm_module_t* module = wasm_module_new(store, &binary);
  if (!module) {
    printf("> Error compiling module!\n");
    return 1;
  }

  wasm_byte_vec_delete(&binary);

  return 0;
}

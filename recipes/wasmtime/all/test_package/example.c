#include <wasmtime.h>

int main() {
  char* wat = "";
  wasm_byte_vec_t ret;
  wasmtime_error_t *error = wasmtime_wat2wasm(wat, sizeof(wat), &ret);
  return 0;
}

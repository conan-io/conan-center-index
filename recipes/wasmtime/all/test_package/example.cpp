#include <thread>
#include <wasmtime.h>

int main() {
  auto wat = "";
  wasm_byte_vec_t ret;
  auto *error = wasmtime_wat2wasm(wat, sizeof(wat), &ret);
  std::this_thread::sleep_for(std::chrono::seconds(1));
  return 0;
}

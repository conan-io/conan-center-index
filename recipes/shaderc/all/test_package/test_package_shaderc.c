#include <shaderc/shaderc.h>

int main() {
  shaderc_compiler_t shaderc_compiler = shaderc_compiler_initialize();
  shaderc_compiler_release(shaderc_compiler);

  return 0;
}

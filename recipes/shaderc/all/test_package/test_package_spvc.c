#include <shaderc/spvc.h>

int main() {
  shaderc_spvc_compiler_t shaderc_spvc_compiler = shaderc_spvc_compiler_initialize();
  shaderc_spvc_compiler_release(shaderc_spvc_compiler);

  return 0;
}

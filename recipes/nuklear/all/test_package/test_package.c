#define NK_INCLUDE_DEFAULT_ALLOCATOR
#include <nuklear.h>

int main() {
  struct nk_context ctx;
  nk_init_default(&ctx, NULL);

  return 0;
}

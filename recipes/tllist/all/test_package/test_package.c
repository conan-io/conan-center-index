#include <stdlib.h>
#include <tllist.h>

int main(int argc, const char *const *argv) {
  tll(int) l = tll_init();

  tll_push_back(l, 43);

  return EXIT_SUCCESS;
}

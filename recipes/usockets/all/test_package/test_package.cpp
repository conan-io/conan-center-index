#include <stddef.h>
#include <libusockets.h>

int main() {
  struct us_loop_t *loop = us_create_loop(0, NULL, NULL, NULL, 0);
}

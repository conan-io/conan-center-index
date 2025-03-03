#include <fenster.h>
#include <fenster_audio.h>

#define W 320
#define H 240

void dummy() {
  uint32_t buf[W * H];
  struct fenster f = { .title = "hello", .width = W, .height = H, .buf = buf };
  fenster_open(&f);
  fenster_close(&f);
}

int main() {
  return 0;
}

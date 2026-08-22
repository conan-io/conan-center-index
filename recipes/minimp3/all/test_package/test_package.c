#define MINIMP3_IMPLEMENTATION
#include <minimp3.h>

int main() {
  static mp3dec_t mp3d;
  mp3dec_init(&mp3d);

  return 0;
}

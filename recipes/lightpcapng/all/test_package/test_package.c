#include <stdlib.h>
#include "light_pcapng_ext.h"

int main(void) {
  const char* outfile = "conan_test.pcapng";
  light_pcapng writer = light_pcapng_open(outfile, "wb");
  light_pcapng_close(writer);
  return EXIT_SUCCESS;
}


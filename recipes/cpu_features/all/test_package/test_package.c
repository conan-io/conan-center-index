#include <stdlib.h>
#include <stdio.h>
#include <cpuinfo_x86.h>

int main()
{
  X86Features features = GetX86Info().features;
  if (features.aes) {
    printf("AES is available\n");
  } else {
    printf("AES isn't available\n");
  }
  return EXIT_SUCCESS;
}

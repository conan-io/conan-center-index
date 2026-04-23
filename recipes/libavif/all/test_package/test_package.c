#include <avif/avif.h>
#include <stddef.h>
#include <stdio.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  if (!avifCodecName(AVIF_CODEC_CHOICE_AUTO, AVIF_CODEC_FLAG_CAN_DECODE)) {
    printf("No decoder available - there should be at least one. Was libavif "
           "compiled without any codec?\n");
    return 1;
  }

  return 0;
}

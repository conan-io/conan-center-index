#include <avif/avif.h>
#include <stddef.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  if (!avifCodecName(AVIF_CODEC_CHOICE_AUTO, AVIF_CODEC_FLAG_CAN_DECODE))
    return 1;

  return 0;
}

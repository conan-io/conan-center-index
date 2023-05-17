#include <stdio.h>
#include <alsa/global.h>

int main()
{
  printf("libalsa version %s\n", snd_asoundlib_version());
  return 0;
}

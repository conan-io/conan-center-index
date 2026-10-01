#include <stdio.h>
#include <alsa/asoundlib.h>

int main()
{
  printf("libalsa version %s\n", snd_asoundlib_version());
  return 0;
}

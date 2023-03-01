#include <portaudio.h>
#include <stdio.h>

int main() {
  int version = Pa_GetVersion();
  const char* versionText = Pa_GetVersionText();
  printf("PortAudio version %x\n", version);
  printf("%s\n", versionText);
  return 0;
}

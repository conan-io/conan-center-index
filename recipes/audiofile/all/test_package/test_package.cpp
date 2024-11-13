// workaround for a missing include in v1.0.9 and earlier
#include <stdint.h>
#include <iostream>
#include <limits>
#include <AudioFile.h>



int main(int argc, char **argv) {

  AudioFile<double> audioFile;
  audioFile.load("fake-file.wav");
  audioFile.printSummary();
  return 0;
}

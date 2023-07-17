// workaround for a missing include in v1.0.9 and earlier
#include <limits>

#include <AudioFile.h>

#include <iostream>

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Need at least one argument" << std::endl;
    return 1;
  }

  AudioFile<double> audioFile;
  audioFile.load(argv[1]);
  audioFile.printSummary();
  return 0;
}

#include <iostream>
#include "sndfile.hh"

int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cout << "Usage: example <file.wav>" << std::endl;
	} else {
		SndfileHandle handle(argv[1]);
		std::cout << "Sample rate: " << handle.samplerate() << std::endl;
	}
	return 0;
}

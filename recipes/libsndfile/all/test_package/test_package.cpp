#include "sndfile.hh"

#if __cplusplus < 201100 && defined(_MSC_VER)
#undef nullptr
#endif

#include <iostream>

int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cout << "Usage: example <file.wav>\n";
	} else {
		SndfileHandle handle(argv[1]);
		std::cout << "Sample rate: " << handle.samplerate() << "\n";
	}
	return 0;
}

#include <cstdlib>
#include <iostream>

#include "FLAC++/encoder.h"

class OurEncoder: public FLAC::Encoder::File {
public:
	OurEncoder(): FLAC::Encoder::File() {}
protected:
	virtual void progress_callback(FLAC__uint64 bytes_written, FLAC__uint64 samples_written, uint32_t frames_written, uint32_t total_frames_estimate)
    {}
};

int main()
{
    OurEncoder encoder;
    if(!encoder) {
		return EXIT_FAILURE;
	}
    return EXIT_SUCCESS;
}

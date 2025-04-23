#include <msgpack23/msgpack23.h>

int main(void) {
	
    msgpack23::Packer packer {};
	std::uint8_t const expected = 42;
	auto data = packer(expected);
	msgpack23::Unpacker unpacker {data};
	std::int8_t actual {};
	unpacker(actual);
	
    return EXIT_SUCCESS;
}

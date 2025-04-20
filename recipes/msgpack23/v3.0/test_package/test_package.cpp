#include <msgpack23/msgpack23.h>
#include <vector>
#include <iterator>

int main(void) {
	std::vector<std::byte> data{};
	auto inserter = std::back_inserter(data);
    msgpack23::Packer packer {inserter};
	std::uint8_t const expected = 42;
	packer(expected);
	msgpack23::Unpacker unpacker {data};
	std::int8_t actual {};
	unpacker(actual);
	
    return EXIT_SUCCESS;
}

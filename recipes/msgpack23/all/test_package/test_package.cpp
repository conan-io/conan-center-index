#include <msgpack23/msgpack23.h>
#include <vector>
#include <iostream>

int main(void) {
	std::vector<std::byte> packedData{};
	msgpack23::Unpacker unpacker(packedData);
	std::cout << "msgpack23 test package" << std::endl;
    return EXIT_SUCCESS;
}

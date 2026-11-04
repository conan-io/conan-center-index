#include <cstdlib>
#include <iostream>
#include "CRC.h"


int main(void) {
	const char myString[] = { 'H', 'E', 'L', 'L', 'O', ' ', 'W', 'O', 'R', 'L', 'D' };
	
	std::uint32_t crc = CRC::Calculate(myString, sizeof(myString), CRC::CRC_32());
	
	std::cout << std::hex << crc;
	
	return 0;
}

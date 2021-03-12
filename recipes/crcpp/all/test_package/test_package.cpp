#include <iostream>

#include "CRC.h"

int main(int argc, char ** argv)
{
	const char myString[] = { 'H', 'E', 'L', 'L', 'O', ' ', 'W', 'O', 'R', 'L', 'D'};
	
	std::uint32_t crc = CRC::Calculate(myString, sizeof(myString), CRC::CRC_32());
	
    std::cout << ( (crc == 0x87e5865b) ? "It works!" : "Something's wrong!");
	
	return 0;
}

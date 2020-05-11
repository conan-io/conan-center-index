#include <iostream>
#include "bitserializer/bit_serializer.h"

int main() {
	std::cout << "BitSerializer version: "
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Major) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Minor) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Maintenance)
		<< std::endl;
}

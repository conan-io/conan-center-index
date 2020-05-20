#include <iostream>
#include <filesystem>
#include "bitserializer/bit_serializer.h"

int main() {
	std::cout << "BitSerializer version: "
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Major) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Minor) << "."
		<< BitSerializer::Convert::To<std::string>(BitSerializer::Version::Maintenance)
		<< std::endl;
	// Some compilers does not link filesystem automatically
	std::cout << "Testing the link of C++17 filesystem: " << std::filesystem::temp_directory_path() << std::endl;
}

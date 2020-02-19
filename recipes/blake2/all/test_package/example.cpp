#include <array>
#include <iomanip>
#include <iostream>
#include <blake2.h>

int main() {

 	const std::string input = "Conan";
    const std::string key = "C++";
    const std::string expected_hash = "aff48ebab1a2b9947c811248b52a157738159af3a2599993188fd3977d20c58e67a98636717e13b62b95183ff779abdb2dcad039599f5e54588d83a7b2fc3827";
    std::array<unsigned char, BLAKE2B_OUTBYTES> output;
    int result; // Zero if OK

	result = blake2(output.data(), output.size(), input.data(), input.size(), key.data(), key.size());

    std::cout << "Hashing string: " << input.data() << std::endl;
    std::cout << "Using key: " << key.data() << std::endl;
    std::cout << "Expected hash: " << expected_hash.data() << std::endl;

    if (result != 0){
        std::cout << "Error during hashing";
    } else {
        std::cout << "Computed hash: ";
	    std::cout << std::setfill('0') << std::hex;
	    for (auto byte : output)
	    	std::cout << std::setw(2) << static_cast<unsigned>(byte);
	    std::cout << std::endl;
    }
}

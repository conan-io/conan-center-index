#include <iostream>
#include "picosha2.h"

void CalcAndOutput(const std::string& src){
	std::cout << "src : \"" << src << "\"\n";
	std::cout << "hash: " << picosha2::hash256_hex_string(src) << "\n" << std::endl;
}

int main(int argc, char* argv[])
{
    CalcAndOutput("");

    return 0;
}

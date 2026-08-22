#include "Poco/Hash.h"
#include <iostream>


int main() {
	std::cout << "Poco Foundation: " << Poco::hash("Hello Conan!") << std::endl;
	return 0;
}

#include "Poco/Util/Option.h"
#include "Poco/Util/OptionSet.h"
#include <iostream>


int main(void) {
	Poco::Util::Option option("conan", "c", "validate Poco::Util");
	std::cout << "Poco Util Option: " << option.fullName() << std::endl;
	return 0;
}
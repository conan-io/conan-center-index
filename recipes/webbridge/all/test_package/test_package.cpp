#include "webbridge/object.h"

#include <iostream>
#include <string>

class Greeter : public webbridge::object {
public:
	std::string greet(const std::string& name) { return "Hello, " + name + "!"; }
};

int main() {
	Greeter g;
	std::cout << g.greet("Conan") << "\n";
	return 0;
}

#include <cstdlib>
#include <iostream>
#include <simple-yaml/simple_yaml.hpp>

struct Test : public simple_yaml::Simple {
	using Simple::Simple;

	int         a = bound("a");
	std::string b = bound("b");
};

const std::string source{R"(
a: 1
b: hello
)"};

int main() {
	Test test{simple_yaml::fromString(source)};

	return test.a == 1 && test.b == "hello" ? EXIT_SUCCESS : EXIT_FAILURE;
}

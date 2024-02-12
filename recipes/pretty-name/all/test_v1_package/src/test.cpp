#include <cstdlib>
#include <iostream>
#include <pretty-name/pretty_name.hpp>

struct Test {
	int a;
	int b;
};

namespace Namespace {
template<typename A, typename B>
struct Test {
	A a;
	B b;
};
} // namespace Namespace

int main() {
	std::cout << pretty_name::pretty_name<Test>() << std::endl;
	std::cout << pretty_name::pretty_name<Namespace::Test<double, Test>>() << std::endl;

	return EXIT_SUCCESS;
}

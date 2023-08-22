#include <cstdlib>
#include <source_location>

int main() {
	constexpr auto loc = std::source_location::current();

	return loc.line() == 5 ? EXIT_SUCCESS : EXIT_FAILURE;
}

#include <bigint23/bigint.hpp>
#include <iostream>

int main(void) {
	bigint::bigint<bigint::BitWidth{128}, bigint::Signedness::Unsigned> const value = 0x12345678;
	std::cout << value << '\n';
    return EXIT_SUCCESS;
}

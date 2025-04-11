#include <bigint23/bigint23.h>
#include <iostream>

int main(void) {
	bigint23::bigint23<128, false> const value = 0x12345678;
	std::cout << value << '\n';
    return EXIT_SUCCESS;
}

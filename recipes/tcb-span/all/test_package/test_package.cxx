#include <tcb/span.hpp>

#include <array>
#include <cstddef>
#include <cstdio>
#include <vector>

std::ptrdiff_t size(tcb::span<const int> s)
{
	return s.size();
}

int main(void)
{
	int                carr[3] = {1, 3, 4};
	std::array<int, 2> cxxarr = {1, 2};

	printf("C-array: %ti\n", size(carr));
	printf("array:   %ti\n", size(cxxarr));

	return 0;
}

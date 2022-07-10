#include <array>
#include <gsl/gsl>

int main() 
{
	std::array<int, 5> data{{1, 2, 3, 4, 5}};
	gsl::span<int, 5> span(data); 
	if (span.size() != 5) {
		return 1;
	}
	return 0;
}

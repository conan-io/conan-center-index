#include <cotila/cotila.h>

int main() {
	constexpr cotila::matrix<double, 2, 3> m1 {{{1., 2., 3.}, {4., 5., 6.}}}; // very explicit declaration
	constexpr cotila::matrix m2 {{{1., 4.}, {2., 5.}, {3., 6.}}}; // deduces the type, but the extra braces are required
	static_assert(m2 == cotila::transpose(m1));
}

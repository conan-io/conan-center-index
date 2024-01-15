#include <ios>
#include <iostream>

#include <dice/template-library/integral_template_tuple.hpp>

#ifdef DICE_TEMPLATE_LIBRARY_1_0_0_LATER
template<std::size_t N>
struct int_array : std::array<int, N> {
private:
	template<std::size_t... IDs>
	int_array(int value, std::index_sequence<IDs...>) : std::array<int, N>{((void) IDs, value)...} {}

public:
	int_array() = default;
	int_array(int value) : int_array(value, std::make_index_sequence<N>{}) {}
};

template<std::size_t N>
std::ostream &operator<<(std::ostream &os, int_array<N> const &arr) {
	if (N == 0) { return os << "0: []"; }
	os << N << ": [";
	for (std::size_t i = 0; i < N - 1; ++i) { os << arr[i] << ", "; }
	return os << arr[N - 1] << ']';
}

int main() {
    dice::template_library::integral_template_tuple<5UL, 8, int_array> itt;
    std::cout << "  " << itt.template get<5>() << '\n';
}

#else

template <int N> struct Wrapper {
    static constexpr int i = N;
};

int main() {
    dice::template_library::integral_template_tuple<Wrapper, 0, 5> tup;
    std::cout << std::boolalpha << "tup.get<3>().i == 3: " << (tup.get<3>().i == 3) << std::endl;
}
#endif

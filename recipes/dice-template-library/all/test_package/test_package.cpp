#include <dice/template-library/integral_template_tuple.hpp>

#include <ios>
#include <iostream>

template <int N> struct Wrapper { static constexpr int i = N; };

int main() {
    dice::template_library::integral_template_tuple<Wrapper, 0, 5> tup;
    std::cout << std::boolalpha << "tup.get<3>().i == 3: " << (tup.get<3>().i == 3) << std::endl;
}

#include <flux.hpp>

int main() {
    constexpr auto result = flux::from(std::array{1, 2, 3, 4, 5})
                             .filter(flux::pred::even)
                             .map([](int i) { return i * 2; })
                             .sum();
    static_assert(result == 12);
}

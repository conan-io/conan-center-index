#include <iostream>

#include <tweeners/builder.hpp>
#include <tweeners/easing.hpp>
#include <tweeners/system.hpp>

auto main([[maybe_unused]] int argc, [[maybe_unused]] char* argv[]) -> int {
    std::cout << std::boolalpha;
    std::cin.tie(nullptr);
    std::ios_base::sync_with_stdio(false);

    constexpr auto from = 0;
    constexpr auto to = 100;
    constexpr auto duration = 10.f;

    auto system = tweeners::system {};

    auto x = 0;
    tweeners::builder().range_transform(from, to, duration, x, tweeners::easing::sine<>).build(system);

    for (auto i = 0; i != 10; ++i) {
        system.update(1.0f);
        std::cout << i << "->" << x << std::endl;
    }

    return 0;
}

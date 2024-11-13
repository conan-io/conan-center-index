#include <cstdlib>
#include <rocket.hpp>
#include <iostream>

int main()
{
    rocket::signal<int(int)> test;
    test.connect([](int x)
                 { return x * 3; });

    constexpr int value = 2;

    const auto result{test(value) == value * 3};
    std::cout << "Rocket test success: " << std::boolalpha << result << '\n';
    return result? EXIT_SUCCESS : EXIT_FAILURE;
}

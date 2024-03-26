#include <cstdlib>

#include "rocket.hpp"

int main()
{
    rocket::signal<int(int)> test;
    test.connect([](int x)
                 { return x * 3; });

    constexpr int value = 2;
    return test(value) == value*3 ? EXIT_SUCCESS : EXIT_FAILURE;
}

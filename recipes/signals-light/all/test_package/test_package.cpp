#include <iostream>
#include "signals_light/signal.hpp"

int main(void) {
    auto signal = sl::Signal<void(int)>{};
    signal.connect([](int i){ std::cout << i << '\n'; });
    signal.connect([](int i){ std::cout << i * 2 << '\n'; });

    signal(4);  // prints "4\n8\n" to standard output.
}

#include <iostream>
#include <dylib.hpp>

int main()
{
    try {
        dylib lib("foo");
        std::cerr << "Expected dylib::load_error exception" << std::endl;
        return 1;
    } catch (const dylib::load_error &) {
        return 0;
    }
}

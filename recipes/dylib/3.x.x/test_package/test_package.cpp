#include <iostream>
#include <dylib.hpp>

int main()
{
    try {
        dylib::library lib("./foo", dylib::decorations::os_default());
        std::cerr << "Expected dylib::load_error exception" << std::endl;
        return 1;
    } catch (const dylib::load_error &) {
        return 0;
    }
}

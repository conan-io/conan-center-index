#include <iostream>
#include <tuple>

#include <msgpack.hpp>

int main() {
    msgpack::object obj(123);
    std::cout << obj << "\n";
    return 0;
}

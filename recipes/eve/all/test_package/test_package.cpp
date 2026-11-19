#include <eve/module/core.hpp>
#include <eve/wide.hpp>

#include <cassert>
#include <iostream>

int main() {
    eve::wide<float> x{1.0f, 2.0f, 3.0f, 4.0f};
    eve::wide<float> y{5.0f, 6.0f, 7.0f, 8.0f};
    auto z = eve::add(x, y);
    std::cout << "eve::add result: " << z << "\n";
    assert(eve::all(z >= 6.0f));
    return 0;
}

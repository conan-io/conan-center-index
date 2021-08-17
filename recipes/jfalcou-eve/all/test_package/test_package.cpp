#include <eve/eve.hpp>
#include <iostream>

int main()
{
    eve::wide<float, eve::fixed<4>> p{1.f,2.f,3.f,4.f};
    std::cout << "eve test: " << p + 10 * p << "\n";
    return 0;
}

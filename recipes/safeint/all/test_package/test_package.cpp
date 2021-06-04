#include <SafeInt.hpp>

int main() {
    SafeInt<int> i1(1);
    SafeInt<int> i2(2);
    auto i3 = i1 + i2;
    return 0;
}

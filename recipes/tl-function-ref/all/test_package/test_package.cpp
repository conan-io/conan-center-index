#include <tl/function_ref.hpp>

#include <iostream>

bool f_called = false;
void f() {
    f_called = true;
}

int main() {
    std::cout << f_called << std::endl;
    tl::function_ref<void(void)> fr = f;
    fr();
    std::cout << f_called << std::endl;

    return 0;
}

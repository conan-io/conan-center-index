#include <iostream>
#include "seq/devector.hpp"

int main(void) {
    seq::devector<int> vec;

    vec.emplace_front(5);
    vec.emplace_front(3);
    vec.emplace_front(9);
    vec.emplace_front(4);
    vec.emplace_front(8);
    vec.emplace_front(1);

    return EXIT_SUCCESS;
}

#include <iostream>

#include "itoa/jeaiii_to_text.h"

template <typename T>
void itoa(T n, char* b) {
    *jeaiii::to_text_from_integer(b, n) = '\0';
}

template <typename T>
void show(T n) {
    char text[32];
    itoa(n, text);
    std::cout << text << "\n";
}

int main(void) {
    show(-1);
    show(1 << 31);
    show(0x7fffffff);
    show(-0x7fffffff - 1);
    show(17999999999999999999ULL);
    show(-5999999999999999999LL);

    return 0;
}

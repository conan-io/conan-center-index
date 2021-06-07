#include <vectorclass.h>

#include <iostream>

int main() {
    Vec4i a(10, 11, 12, 13);
    Vec4i b(20, 21, 22, 23);

    Vec4i c = a + b;
    for (int i = 0; i < c.size(); ++i) {
        std::cout << " " << c[i];
    }
    std::cout << std::endl;

    return 0;
}

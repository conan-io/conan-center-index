#include <pdqsort.h>

#include <iostream>

int main() {
    int v[10] = {3, -102, 4, 30, 432, -13531, -43, 1, 0, -3};

    pdqsort(v, v + 10);
    for (int i = 0; i < 10; ++i) {
        std::cout << v[i] << ' ';
    }
    std::cout << std::endl;

    return 0;
}

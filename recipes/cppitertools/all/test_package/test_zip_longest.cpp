#include <iostream>
#include <vector>
#include <cppitertools/zip_longest.hpp>


int main() {
    std::vector<int> v1 = {0, 1, 2, 3};
    std::vector<int> v2 = {10, 11};
    for (auto&& [x, y] : iter::zip_longest(v1, v2)) {
        std::cout << '{';
        if (x) {
            std::cout << "Just " << *x;
        } else {
            std::cout << "Nothing";
        }
        std::cout << ", ";
        if (y) {
            std::cout << "Just " << *y;
        } else {
            std::cout << "Nothing";
        }
        std::cout << "}\n";
    }

    return 0;
}

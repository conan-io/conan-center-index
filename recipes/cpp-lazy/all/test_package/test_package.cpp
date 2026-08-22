#include <iostream>

#define LZ_STANDALONE
#include <Lz/Map.hpp>

int main() {
    std::array<int, 4> arr = {1, 2, 3, 4};
    std::string result = lz::map(arr, [](int i) { return i + 1; }).toString(" ");  // == "2 3 4 5"

    std::cout << result << "\n";

    return 0;
}

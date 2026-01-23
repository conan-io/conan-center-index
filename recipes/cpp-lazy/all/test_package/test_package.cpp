#include <iostream>

#define LZ_STANDALONE
#ifdef CPP_LAZY_9_0_0_NEWER
#  include <Lz/map.hpp>
#  include <Lz/stream.hpp>
#else
#  include <Lz/Map.hpp>
#endif

int main() {
    std::array<int, 4> arr = {1, 2, 3, 4};
#ifdef CPP_LAZY_9_0_0_NEWER
    std::string result = "";
    for (auto i : lz::map(arr, [](int i) { return i + 1; })) {
        result += std::to_string(i) + " ";
    }
#else
    std::string result = lz::map(arr, [](int i) { return i + 1; }).toString(" ");  // == "2 3 4 5"
#endif
    std::cout << result << "\n";

    return 0;
}

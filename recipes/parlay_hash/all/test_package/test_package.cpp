#include <parlay_hash/unordered_map.h>

#include <iostream>

auto main() -> int {
    auto map = parlay::unordered_map<int, std::string>();
    map[123] = "hello";
    map[987] = "world!";

    for (auto const& [key, val] : map) {
        std::cout << key << " => " << val << std::endl;
    }
}

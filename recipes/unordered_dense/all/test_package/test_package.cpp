// sited from https://github.com/martinus/unordered_dense/blob/main/example/main.cpp
#include <ankerl/unordered_dense.h>

#include <iostream>

auto main() -> int {
    auto map = ankerl::unordered_dense::map<int, std::string>();
    map[123] = "hello";
    map[987] = "world!";

    for (auto const& [key, val] : map) {
        std::cout << key << " => " << val << std::endl;
    }
}

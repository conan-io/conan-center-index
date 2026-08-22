#include <cstdint>
#include <iostream>
#include <string>
#include <tsl/sparse_map.h>
#include <tsl/sparse_set.h>

int main() {
    tsl::sparse_map<std::string, int> map = {{"a", 1}, {"b", 2}};
    map["c"] = 3;
    map["d"] = 4;

    map.insert({"e", 5});
    map.erase("b");

    for(auto it = map.begin(); it != map.end(); ++it) {
        //it->second += 2; // Not valid.
        it.value() += 2;
    }

    // {d, 6} {a, 3} {e, 7} {c, 5}
    for(const auto& key_value : map) {
        std::cout << "{" << key_value.first << ", " << key_value.second << "}" << std::endl;
    }


    if(map.find("a") != map.end()) {
        std::cout << "Found \"a\"." << std::endl;
    }

    const std::size_t precalculated_hash = std::hash<std::string>()("a");
    // If we already know the hash beforehand, we can pass it as argument to speed-up the lookup.
    if(map.find("a", precalculated_hash) != map.end()) {
        std::cout << "Found \"a\" with hash " << precalculated_hash << "." << std::endl;
    }

    tsl::sparse_set<int> set;
    set.insert({1, 9, 0});
    set.insert({2, -1, 9});

    // {0} {1} {2} {9} {-1}
    for(const auto& key : set) {
        std::cout << "{" << key << "}" << std::endl;
    }
}

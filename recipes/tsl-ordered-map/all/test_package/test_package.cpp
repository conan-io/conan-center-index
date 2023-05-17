#include <iostream>
#include <string>
#include <cstdlib>
#include <tsl/ordered_map.h>
#include <tsl/ordered_set.h>

int main() {
    tsl::ordered_map<char, int> map = {{'d', 1}, {'a', 2}, {'g', 3}};
    map.insert({'b', 4});
    map['h'] = 5;
    map['e'] = 6;

    map.erase('a');

    // {d, 1} {g, 3} {b, 4} {h, 5} {e, 6}
    for(const auto& key_value : map) {
        std::cout << "{" << key_value.first << ", " << key_value.second << "}" << std::endl;
    }

    map.unordered_erase('b');
    
    // Break order: {d, 1} {g, 3} {e, 6} {h, 5}
    for(const auto& key_value : map) {
        std::cout << "{" << key_value.first << ", " << key_value.second << "}" << std::endl;
    }

    for(auto it = map.begin(); it != map.end(); ++it) {
        //it->second += 2; // Not valid.
        it.value() += 2;
    }

    if(map.find('d') != map.end()) {
        std::cout << "Found 'd'." << std::endl;
    }

    const std::size_t precalculated_hash = std::hash<char>()('d');
    // If we already know the hash beforehand, we can pass it as argument to speed-up the lookup.
    if(map.find('d', precalculated_hash) != map.end()) {
        std::cout << "Found 'd' with hash " << precalculated_hash << "." << std::endl;
    }

    tsl::ordered_set<char, std::hash<char>, std::equal_to<char>, std::allocator<char>, std::vector<char>> set;
    set.reserve(6);

    set = {'3', '4', '9', '2'};
    set.erase('2');
    set.insert('1');
    set.insert('\0');
    
    set.pop_back();
    set.insert({'0', '\0'});

    // Get raw buffer for C API: 34910
    std::cout << atoi(set.data()) << std::endl;
}

#include <iostream>
#include <tsl/array_map.h>
#include <tsl/array_set.h>

int main() {
    // Map of const char* to int
    tsl::array_map<char, int> map = {{"one", 1}, {"two", 2}};
    map["three"] = 3;
    map["four"] = 4;

    map.insert("five", 5);
    map.insert_ks("six_with_extra_chars_we_ignore", 3, 6);

    map.erase("two");

    // When template parameter StoreNullTerminator is true (default) and there is no
    // null character in the strings.
    for(auto it = map.begin(); it != map.end(); ++it) {
        std::cout << "{" << it.key() << ", " << it.value() << "}" << std::endl;
    }

    // If StoreNullTerminator is false for space efficiency or you are storing null characters, 
    // you can access to the size of the key.
    for(auto it = map.begin(); it != map.end(); ++it) {
        (std::cout << "{").write(it.key(), it.key_size()) << ", " << it.value() << "}" << std::endl;
    }

    // Or if you just want the values.
    for(int value: map) {
        std::cout << "{" << value << "}" << std::endl;
    }

    // Map of const char32_t* to int
    tsl::array_map<char32_t, int> map_char32 = {{U"one", 1}, {U"two", 2}};
    map_char32[U"three"] = 3;

    // Set of const char*
    tsl::array_set<char> set = {"one", "two", "three"};
    set.insert({"four", "five"});

    for(auto it = set.begin(); it != set.end(); ++it) {
        std::cout << "{" << it.key() << "}" << std::endl;
    }
}

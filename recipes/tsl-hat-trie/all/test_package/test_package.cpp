#include <iostream>
#include <string>
#include <tsl/htrie_map.h>
#include <tsl/htrie_set.h>

int main() {
    /*
     * Map of strings to int having char as character type. 
     * There is no support for wchar_t, char16_t or char32_t yet, 
     * but UTF-8 strings will work fine.
     */
    tsl::htrie_map<char, int> map = {{"one", 1}, {"two", 2}};
    map["three"] = 3;
    map["four"] = 4;

    map.insert("five", 5);
    map.insert_ks("six_with_extra_chars_we_ignore", 3, 6);
    
    map.erase("two");

    /*
     * Due to the compression on the common prefixes, the letters of the string 
     * are not always stored contiguously. When we retrieve the key, we have to 
     * construct it.
     * 
     * To avoid a heap-allocation at each iteration (when SSO doesn't occur), 
     * we reuse the key_buffer to construct the key.
     */
    std::string key_buffer;
    for(auto it = map.begin(); it != map.end(); ++it) {
        it.key(key_buffer);
        std::cout << "{" << key_buffer << ", " << it.value() << "}" << std::endl;
    }

    /*
     * If you don't care about the allocation.
     */
    for(auto it = map.begin(); it != map.end(); ++it) {
        std::cout << "{" << it.key() << ", " << *it << "}" << std::endl;
    }

    tsl::htrie_map<char, int> map2 = {{"apple", 1}, {"mango", 2}, {"apricot", 3},
                                      {"mandarin", 4}, {"melon", 5}, {"macadamia", 6}};

    // Prefix search
    auto prefix_range = map2.equal_prefix_range("ma");

    // {mandarin, 4} {mango, 2} {macadamia, 6}
    for(auto it = prefix_range.first; it != prefix_range.second; ++it) {
        std::cout << "{" << it.key() << ", " << *it << "}" << std::endl;
    }

    // Find longest match prefix.
    auto longest_prefix = map2.longest_prefix("apple juice");
    if(longest_prefix != map2.end()) {
        // {apple, 1}
        std::cout << "{" << longest_prefix.key() << ", " 
                  << *longest_prefix << "}" << std::endl;
    }

    // Prefix erase
    map2.erase_prefix("ma");

    // {apricot, 3} {melon, 5} {apple, 1}
    for(auto it = map2.begin(); it != map2.end(); ++it) {
        std::cout << "{" << it.key() << ", " << *it << "}" << std::endl;
    }

    tsl::htrie_set<char> set = {"one", "two", "three"};
    set.insert({"four", "five"});

    // {one} {two} {five} {four} {three}
    for(auto it = set.begin(); it != set.end(); ++it) {
        it.key(key_buffer);
        std::cout << "{" << key_buffer << "}" << std::endl;
    }
}

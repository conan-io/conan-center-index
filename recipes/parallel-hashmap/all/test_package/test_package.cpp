#include <parallel_hashmap/phmap.h>

#include <iostream>
#include <string>

using phmap::flat_hash_map;

int main() {
    // Create an unordered_map of three strings (that map to strings)
    flat_hash_map<std::string, std::string> email = {
        {"tom",  "tom@gmail.com"},
        {"jeff", "jk@gmail.com"},
        {"jim",  "jimg@microsoft.com"}
    };

    // Iterate and print keys and values
    for (const auto &n : email) {
        std::cout << n.first << "'s email is: " << n.second << "\n";
    }

    // Add a new entry
    email["bill"] = "bg@whatever.com";

    // and print it
    std::cout << "bill's email is: " << email["bill"] << "\n";

    return 0;
}

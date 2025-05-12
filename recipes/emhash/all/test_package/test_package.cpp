#include <cstdlib>
#include <iostream>
#include <bitset>
#include <string>
#include <vector>

#define EMH_EXT
#include "hash_table5.hpp"

int main(void) {
    // constructor
    emhash5::HashMap<int, int> m1(4);
    m1.reserve(100);
    for (int i = 1; i < 100; i++)
        m1.emplace_unique(i, i); //key must be unique, performance is better than emplace, operator[].

    auto no_value = m1.at(0); //no_value = 0; no exception throw!!!. only return zero for integer value.

    // list constructor
    emhash5::HashMap<int, std::string> m2 = {
        {1, "foo"},
        {3, "bar"},
        {2, "baz"},
    };

    auto* pvalue = m2.try_get(1); //return nullptr if key is not exist
    if (m2.try_set(4, "for"))   printf("set success");
    if (!m2.try_set(1, "new"))  printf("set failed");
    std::string ovalue = m2.set_get(1, "new"); //ovalue = "foo" and m2[1] == "new"

    for(auto& p: m2)
        std::cout << " " << p.first << " => " << p.second << '\n';

    // copy constructor
    emhash5::HashMap<int, std::string> m3 = m2;
    // move constructor
    emhash5::HashMap<int, std::string> m4 = std::move(m2);

    //insert. insert_unique. emplace
    m2.insert_unique(4, "four");
    m2[4] = "four_again";
    m2.emplace(std::make_pair(4, "four"));
    m2.insert({{6, "six"}, {5, "five"}});

    // range constructor
    std::vector<std::pair<std::bitset<8>, int>> v = { {0x12, 1}, {0x01,-1} };
    emhash5::HashMap<std::bitset<8>, double> m5(v.begin(), v.end());
}

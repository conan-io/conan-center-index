#include <iostream>
#include <string>
#include <cppitertools/itertools.hpp>

namespace {
    int length(const std::string& s) {
        return s.size();
    }
}


int main() {
    const std::vector<std::string> vec = {"hi", "ab", "ho", "abc", "def", "abcde", "efghi"};
    std::vector<int> keys;
    std::vector<std::vector<std::string>> groups;

    for (auto&& gb : iter::groupby(vec, length)) {
        keys.push_back(gb.first);
        groups.emplace_back(std::begin(gb.second), std::end(gb.second));
    }

    for (auto&& [i, gb] : iter::enumerate(groups)) {
        std::cout << "Group " << i << ": ";
        for (auto&& [j, e] : iter::enumerate(gb)) {
            std::cout << " - " << j << ": " << e << '\n';
        }
    }
    return 0;
}

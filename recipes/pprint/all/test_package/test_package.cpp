#include <pprint.hpp>

#include <iostream>
#include <set>
#include <vector>

int main() {
    pprint::PrettyPrinter printer(std::cout);
    printer.print(std::vector<std::vector<int>>{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});

    printer.compact(true);
    printer.print(std::set<std::set<int>>{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});

    return 0;
}

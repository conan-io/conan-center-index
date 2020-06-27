#include <robin_hood.h>
#include <iostream>

int main() {

    const robin_hood::unordered_map<int, int> map = {{1,1}};
    const robin_hood::unordered_flat_map<int, int> flat_map = {{1,1}};
    const robin_hood::unordered_node_map<int, int> node_map = {{1,1}};
    const robin_hood::unordered_set<int> set = {1,1};

    std::cout << "robin-hood-hashing test success.\n";
}

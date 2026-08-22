#include <plf_colony.h>

#include <iostream>

int main() {
    plf::colony<int> i_colony;

    // Insert 100 ints:
    for (int i = 0; i != 100; ++i) {
        i_colony.insert(i);
    }

    // Erase half of them:
    for (plf::colony<int>::iterator it = i_colony.begin(); it != i_colony.end(); ++it) {
        it = i_colony.erase(it);
    }

    // Total the remaining ints:
    int total = 0;

    for (plf::colony<int>::iterator it = i_colony.begin(); it != i_colony.end(); ++it) {
        total += *it;
    }

    std::cout << "Total: " << total << std::endl;
    return 0;
}

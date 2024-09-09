#include <annoy/annoylib.h>
#include <annoy/kissrandom.h>

#include <iostream>
#include <vector>

int main() {
    const int n = 3;
    Annoy::AnnoyIndex<int, double, Annoy::Angular, Annoy::Kiss32Random, Annoy::AnnoyIndexSingleThreadedBuildPolicy> index(n);

    double x[3][3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    double needle[3] = {0.1, 0.1, 0.8};

    for (int i = 0; i < n; i++) {
        index.add_item(i, x[i]);
    }
    index.build(-1);

    std::vector<int> result;
    index.get_nns_by_vector(needle, 1, -1, &result, nullptr);
    std::cout << "Nearest neighbor to vector [1.0, 0.5, 0.5]: ";
    for (int i : result) {
        std::cout << i << " ";
    }
    std::cout << std::endl;
    return 0;
}

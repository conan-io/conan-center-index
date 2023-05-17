#include <plf_indiesort.h>

#include <vector>

int main() {
    std::vector<int> vec;
    for (int i = 0; i < 60; ++i) {
        vec.push_back(60 - i);
    }
    plf::indiesort(vec);
    return 0;
}

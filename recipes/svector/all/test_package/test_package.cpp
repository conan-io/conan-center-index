#include "ankerl/svector.h"

int main(void) {
    auto vec = ankerl::svector<int, 10>();
    for (int i = 0; i < 100; ++i) {
        vec.push_back(i);
    }
    auto data = vec.data();

    return 0;
}

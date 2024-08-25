#include "daw/daw_bounded_array.h"

int main() {
    daw::array<int, 6> t = { 1, 2, 3, 4, 5, 6 };

    auto val = t[3];

    return 0;
}

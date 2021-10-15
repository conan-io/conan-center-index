#include "daw/daw_carray.h"

int main() {
    daw::carray<int, 6> t = { 1, 2, 3, 4, 5, 6 };

    auto val = t[3];

    return 0;
}

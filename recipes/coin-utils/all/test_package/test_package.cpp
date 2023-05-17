#include "CoinPackedVector.hpp"

#include <cstdio>
#include <cstdlib>

static void check(const char *s, int v) {
    if (!v) {
        fprintf(stderr, "FAIL: %s\n", s);
        exit(1);
    }
}

#define STR(V) #V
#define CHECK(V) check(STR(V), (V))

int main () {
    const int ne = 4;
    const int inx[ne] =   {  1,   4,  0,   2 };
    const double el[ne] = { 10., 40., 1., 50. };

    CoinPackedVector r(ne, inx, el);

    CHECK(r.getIndices()[0] == 1);
    CHECK(r.getIndices()[1] == 4);
    CHECK(r.getIndices()[2] == 0);

    r.sortIncrElement();

    CHECK(r.getIndices()[0] == 0);
    CHECK(r.getIndices()[1] == 1);
    CHECK(r.getIndices()[2] == 4);

    r.sortOriginalOrder();

    CHECK(r.getIndices()[0] == 1);
    CHECK(r.getIndices()[1] == 4);
    CHECK(r.getIndices()[2] == 0);

    return 0;
}

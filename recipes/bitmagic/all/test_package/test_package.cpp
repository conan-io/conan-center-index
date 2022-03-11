#include <bm.h>

int main() {
    bm::bvector<> bv_A{1, 2, 3};
    bm::bvector<> bv_B{1, 2, 4};
    bv_A.combine_operation(bv_B, bm::BM_OR);
    return 0;
}

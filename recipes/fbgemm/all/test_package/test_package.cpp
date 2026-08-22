#include <vector>
#include <fbgemm/Fbgemm.h>

int main() {
    auto data = std::vector<std::int8_t>{1, 2, 3, 4, 5, 6};
    fbgemm::PackBMatrix<std::int8_t> matrix(fbgemm::matrix_op_t::Transpose, 3, 2, data.data(), 3);
    matrix.printPackedMatrix("Packed Matrix");
    return 0;
}

#include <fbgemm/Fbgemm.h>

#include <cstdint>
#include <iostream>
#include <vector>

int main() {
  std::vector<std::int8_t> bint8{8, 2, 92, -45, 2, -4};
  fbgemm::PackBMatrix<std::int8_t> packedBN(fbgemm::matrix_op_t::NoTranspose, 2,
                                            3, bint8.data(), 3);
  std::cout << "Offset of the element which was at (1, 2): "
            << packedBN.addr(1, 2) << std::endl;

  return 0;
}

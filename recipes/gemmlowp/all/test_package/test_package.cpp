#include <array>
#include <cstdint>
#include <iostream>

#include <public/gemmlowp.h>

template <typename tScalar, gemmlowp::MapOrder tOrder>
std::ostream& operator<<(std::ostream& s,
                         const gemmlowp::MatrixMap<tScalar, tOrder>& m) {
  for (int i = 0; i < m.rows(); i++) {
    for (int j = 0; j < m.cols(); j++) {
      if (j) {
        s << '\t';
      }
      s << static_cast<float>(m(i, j));
    }
    s << '\n';
  }
  return s;
}

int main() {
  const int rows = 2;
  const int cols = 3;
  const auto kOrder = gemmlowp::MapOrder::RowMajor;

  std::array<uint8_t, rows * cols> lhs{
      1, 2, 3,
      4, 5, 6
  };

  std::array<uint8_t, rows * cols> rhs{
    7, 8,
    9, 10,
    11, 12
  };

  std::array<uint8_t, rows * rows> result{};

  const gemmlowp::MatrixMap<const uint8_t, kOrder> lhs_map(lhs.data(), rows, cols);
  const gemmlowp::MatrixMap<const uint8_t, kOrder> rhs_map(rhs.data(), cols, rows);
  std::cout << "LHS:\n " << lhs_map << "\n";
  std::cout << "RHS:\n " << rhs_map << "\n\n";
  gemmlowp::MatrixMap<uint8_t, kOrder> result_map(result.data(), rows, rows);

  gemmlowp::GemmContext gemm_context{};
  gemmlowp::Gemm<std::uint8_t, gemmlowp::DefaultL8R8BitDepthParams>(
      &gemm_context,
      lhs_map,
      rhs_map,
      &result_map,
      0,
      0,
      0,
      1,
      0);

  std::cout << "Result LHSxRHS: \n" << result_map << std::endl;
  return 0;
}

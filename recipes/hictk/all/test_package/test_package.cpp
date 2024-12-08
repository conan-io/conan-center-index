#include <stdexcept>

#include "hictk/file.hpp"

#if __has_include("hictk/transformers/to_dataframe.hpp")
#include "hictk/transformers/to_dataframe.hpp"     // test hictk/*:with_arrow
#endif

#if __has_include("hictk/transformers/to_dense_matrix.hpp")
#include "hictk/transformers/to_dense_matrix.hpp"  // test hictk/*:with_eigen
#endif

int main(int argc, char** argv) {
  try {
    const hictk::File f(argv[0], 10);  // This is expected to throw
    return 1;
  } catch (const std::exception& e) {
    return 0;
  }
}

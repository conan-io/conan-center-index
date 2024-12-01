#include <stdexcept>

#include "hictk/file.hpp"

#include "hictk/transformers/to_dataframe.hpp"     // test hictk/*:with_arrow
#include "hictk/transformers/to_dense_matrix.hpp"  // test hictk/*:with_eigen


int main(int argc, char** argv) {
  try {
    const hictk::File f(argv[0], 10);  // This is expected to throw
    return 1;
  } catch (const std::exception& e) {
    return 0;
  }
}

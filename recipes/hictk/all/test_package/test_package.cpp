#include <stdexcept>

#include "hictk/balancing/ice.hpp"  // test bshoshany-thread-pool
#include "hictk/chromosome.hpp"
#include "hictk/file.hpp"
#include "hictk/fmt.hpp"  // test formatting of user-defined types with fmt
#include "hictk/genomic_interval.hpp"

#if __has_include("hictk/transformers/to_dataframe.hpp")
#include "hictk/transformers/to_dataframe.hpp"  // test hictk/*:with_arrow
#endif

#if __has_include("hictk/transformers/to_dense_matrix.hpp")
#include "hictk/transformers/to_dense_matrix.hpp"  // test hictk/*:with_eigen
#endif

int main(int argc, char **argv) {
  const hictk::Chromosome chrom(0, "chr1", 123);
  const hictk::GenomicInterval gi(chrom, 10, 20);
  SPDLOG_INFO(FMT_STRING("interval: {}"), gi);

  try {
    const hictk::File f(argv[0], 10);  // This is expected to throw
    return 1;
  } catch (const std::exception &e) {}

  return 0;
}

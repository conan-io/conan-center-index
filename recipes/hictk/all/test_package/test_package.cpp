#include "hictk/chromosome.hpp"
#include "hictk/fmt.hpp"  // test formatting of user-defined types with fmt
#include "spdlog/spdlog.h"
#include "hictk/genomic_interval.hpp"

int main(int argc, char **argv) {
  const hictk::Chromosome chrom(0, "chr1", 123);
  const hictk::GenomicInterval gi(chrom, 10, 20);
  SPDLOG_INFO(FMT_STRING("interval: {}"), gi);

  return 0;
}

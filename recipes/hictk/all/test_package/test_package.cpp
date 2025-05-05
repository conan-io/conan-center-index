#include <fmt/format.h>
#include "hictk/fmt.hpp"
#include "hictk/cooler/utils.hpp"


int main(int argc, char** argv) {
  fmt::print("{}\n", hictk::cooler::utils::is_cooler(argv[0]));
}

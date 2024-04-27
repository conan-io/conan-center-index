#include <stdexcept>

#include "hictk/file.hpp"


int main(int argc, char** argv) {
  try {
    const hictk::File f(argv[0], 10);  // This is expected to throw
    return 1;
  } catch (const std::exception& e) {
    return 0;
  }
}

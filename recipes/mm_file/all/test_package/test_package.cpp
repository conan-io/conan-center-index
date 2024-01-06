#include <iostream>
#include <cinttypes>

#include "mm_file/mm_file.hpp"

int main() {
  std::string filename("tmp.bin");
  static const size_t n = 13;

  {
    // write n uint32_t integers
    mm::file_sink<uint32_t> fout(filename, n);
    std::cout << "mapped " << fout.bytes() << " bytes "
              << "for " << fout.size() << " integers" << std::endl;

    auto *data = fout.data();
    for (uint32_t i = 0; i != fout.size(); ++i) {
      data[i] = i;
      std::cout << "written " << data[i] << std::endl;
    }

    // test iterator
    for (auto x : fout) {
      std::cout << "written " << x << std::endl;
    }

    fout.close();
  }

  return 0;
}

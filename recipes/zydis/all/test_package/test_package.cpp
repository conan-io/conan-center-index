#include <iostream>
#include <Zydis/Zydis.h>


int main(void) {
  const auto version = ZydisGetVersion();
  std::cout << "Zydis version: "
            << ZYDIS_VERSION_MAJOR(version) << '.'
            << ZYDIS_VERSION_MINOR(version) << '.'
            << ZYDIS_VERSION_PATCH(version) << std::endl;
}

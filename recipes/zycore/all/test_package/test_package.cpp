#include <Zycore/Zycore.h>
#include <iostream>

int main(void) {
  const auto version = ZycoreGetVersion();
  std::cout << "Zycore version: "
            << ZYCORE_VERSION_MAJOR(version) << '.'
            << ZYCORE_VERSION_MINOR(version) << '.'
            << ZYCORE_VERSION_PATCH(version) << std::endl;
}

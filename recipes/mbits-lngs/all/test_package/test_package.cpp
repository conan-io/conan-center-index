#include "translations.hpp"
#include <iostream>

int main() {
  lngs::test::Strings tr{};
  tr.init_builtin();
  tr.path_manager<lngs::manager::ExtensionPath>(".", "example");

  std::cout << tr(lngs::test::lng::MESSAGE) << '\n';
}

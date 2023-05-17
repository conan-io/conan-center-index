#include <iostream>
#include <string>

#include "arsenalgear/constants.hpp"
#include "arsenalgear/operators.hpp"

void operators() {
  std::cout << "\n"
            << "======================================================"
            << "\n"
            << "     OPERATORS                                        "
            << "\n"
            << "======================================================"
            << "\n"
            << "\n";

  std::string a = "a";
  std::cout << "Multiplying \"a\" for 5 times: " << a * 5
            << agr::empty_space<std::string_view> * 5 << "adding spaces."
            << "\n\n";
}

int main() {
  operators();
  return 0;
}

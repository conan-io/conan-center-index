#include <cstdlib>
#include <spdlog_setup/spdlog_setup.hpp>
#include <iostream>

int main(void) {
  std::cout << "Welcome to spdlog_setup!\n";
  return 123 == spdlog_setup::details::parse_max_size("123") ? EXIT_SUCCESS : EXIT_FAILURE;
}

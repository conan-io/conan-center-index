#include <emio/emio.hpp>

int main() {
  std::string s = emio::format("{}", 1);
  if (s == "1") {
    return EXIT_SUCCESS;
  }
  return EXIT_FAILURE;
}

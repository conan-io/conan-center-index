#include <fast_float/fast_float.h>

#include <iostream>
#include <string>

int main() {
  const std::string input = "3.1416 xyz ";
  double result;
  auto answer = fast_float::from_chars(input.data(), input.data() + input.size(), result);
  if (answer.ec != std::errc()) {
    std::cerr << "parsing failure\n";
    return 1;
  }
  std::cout << "parsed the number " << result << std::endl;
  return 0;
}

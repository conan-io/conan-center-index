#include "simdjson.h"
#include <iostream>
#include <string>

int main() {
  std::string mystring = "{ \"hello\": \"simdjson\" }";
  simdjson::dom::parser parser;
  std::string_view string_value;
  auto error = parser.parse(mystring)["hello"].get(string_value);
  if (error) {
    std::cerr << error << std::endl;
    return EXIT_FAILURE;
  }
  if (string_value != "simdjson") {
    std::cerr << string_value << std::endl;
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}

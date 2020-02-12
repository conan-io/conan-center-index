#include <iostream>
#include <string>
#include "simdjson/jsonparser.h"

int main() {
  std::string mystring = "{ \"hello\": \"simdjson\" }";
  simdjson::ParsedJson pj = simdjson::build_parsed_json(mystring);
  if (!pj.is_valid()) {
    // something went wrong
    std::cout << pj.get_error_message() << std::endl;
    return 1;
  }
  return 0;
}

#include "sonic/sonic.h"

#include <string>
#include <iostream>

int main()
{
  std::string json = R"(
    {
      "a": 1,
      "b": 2
    }
  )";

  sonic_json::Document doc;
  doc.Parse(json);
  if (doc.HasParseError()) {
    std::cout << "Parse failed!\n";
  } else {
    std::cout << "Parse successful!\n";
  }
  return 0;
}

#include <iostream>
#include <map>
#include <algorithm>

#include "cpp_yyjson.hpp"

using namespace yyjson;

auto json_str = R"(
{
    "id": 1,
    "pi": 3.141592,
    "name": "example",
    "array": [0, 1, 2, 3, 4],
    "currency": {
        "USD": 129.66,
        "EUR": 140.35,
        "GBP": 158.72
    },
    "success": true
})";

int main() {
  // Read JSON string and cast as an object class
  auto obj = *read(json_str).as_object();

  // Key access to the JSON object class
  auto id      = *obj["id"].as_int();
  auto pi      = *obj["pi"].as_real();
  auto name    = *obj["name"].as_string();
  auto success = *obj["success"].as_bool();

  // JSON array/object classes adapt the range concept
  auto list = *obj["array"].as_array();
  for (const auto& v : list) {
    // `write` returns JSON read-only string
    std::cout << v.write() << std::endl;
  }

  // The range value type of object class is a key-value pair
  auto dict = *obj["currency"].as_object();
  for (const auto& [k, v] : dict) {
    std::cout << "{" << k << ": " << v.write() << "}" << std::endl;
  }

  // JSON array/object to container conversion
  auto numbers  = cast<std::vector<int>>(list);
  auto currency = cast<std::map<std::string_view, double>>(dict);

  // Stringify read-only string
  std::cout << obj.write() << std::endl;
}

#include <string>
#include <iostream>

#include "jsonifier/Index.hpp"

struct MyObject {
  std::string name;
  int age;
};

template<> struct jsonifier::core<MyObject> {
	using value_type = MyObject;
	static constexpr auto parseValue = createValue("name", &value_type::name, "age", &value_type::age);
};

int main() {
  MyObject obj("John", 30);
  jsonifier::jsonifier_core jsonifier{};
  std::string jsonBuffer{};
  jsonifier.serializeJson(obj, jsonBuffer);

  std::cout << jsonBuffer << std::endl;

  return 0;
}

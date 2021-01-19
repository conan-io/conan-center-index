#include <iostream>

#include <flags/flags.hpp>

enum class MyEnum { Value1 = 1 << 0, Value2 = 1 << 1 };
ALLOW_FLAGS_FOR_ENUM(MyEnum)

int main() {
  auto mask1 = MyEnum::Value1 | MyEnum::Value2;
  std::cout << mask1.underlying_value() << std::endl;
}

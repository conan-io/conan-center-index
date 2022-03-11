#include <wise_enum.h>

#include <cassert>
#include <iostream>

// Equivalent to enum Color {GREEN = 2, RED};
namespace my_lib {
WISE_ENUM(Color, (GREEN, 2), RED)
}

// Equivalent to enum class MoreColor : int64_t {BLUE, BLACK = 1};
WISE_ENUM_CLASS((MoreColor, int64_t), BLUE, (BLACK, 1))

// Inside a class, must use a different macro, but still works
struct Bar {
  WISE_ENUM_MEMBER(Foo, BUZ)
};

// Adapt an existing enum you don't control so it works with generic code
namespace another_lib {
enum class SomebodyElse { FIRST, SECOND };
}
WISE_ENUM_ADAPT(another_lib::SomebodyElse, FIRST, SECOND)

struct Blub {
    struct Flub {

        int x = 0;

    };
};

int main() {

  // Number of enumerations:
  static_assert(wise_enum::enumerators<my_lib::Color>::size == 2, "");
  std::cerr << "Number of enumerators: "
            << wise_enum::enumerators<my_lib::Color>::size << "\n";

  // Iterate over enums
  std::cerr << "Enum values and names:\n";
  for (auto e : wise_enum::enumerators<my_lib::Color>::range) {
    std::cerr << static_cast<int>(e.value) << " " << e.name << "\n";
  }
  std::cerr << "\n";

  // Convert any enum to a string
  std::cerr << wise_enum::to_string(my_lib::Color::RED) << "\n";

  // Convert any string to an optional enum
  auto x1 = wise_enum::from_string<my_lib::Color>("GREEN");
  auto x2 = wise_enum::from_string<my_lib::Color>("Greeeeeeen");

  assert(x1.value() == my_lib::Color::GREEN);
  assert(!x2);

  // Everything is constexpr, and a type trait is made available for easy use in
  // enable_if/tag dispatch
  static_assert(wise_enum::is_wise_enum<my_lib::Color>::value, "");
  static_assert(!wise_enum::is_wise_enum<int>::value, "");
  enum flub { blub, glub };
  static_assert(!wise_enum::is_wise_enum<flub>::value, "");
  // We made a regular enum wise!
  static_assert(wise_enum::is_wise_enum<another_lib::SomebodyElse>::value, "");

  // Assert underlying type
  static_assert(
      std::is_same<int64_t,
                   typename std::underlying_type<MoreColor>::type>::value,
      "");

  // Full API available for adapted wise enums
  for (auto e : wise_enum::enumerators<another_lib::SomebodyElse>::range) {
    std::cerr << static_cast<int>(e.value) << " "
              << wise_enum::to_string(e.value) << "\n";
  }

  return 0;
}

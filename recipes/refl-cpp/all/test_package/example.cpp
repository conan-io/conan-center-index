#include "refl.hpp"

#include <assert.h>

// The example from the refl-cpp github readme:

struct NonNegative : refl::attr::usage::member {};

struct Point {
  double x, y;
};

REFL_AUTO(type(Point), field(x, NonNegative()), field(y, NonNegative()))

struct Circle {
  Point  origin;
  double radius;
};

REFL_AUTO(type(Circle), field(origin), field(radius, NonNegative()))

template<typename T>
constexpr bool checkNonNegative(const T& obj) {
  // Get the type descriptor for T
  constexpr auto type = refl::reflect<T>();
  // Get the compile-time refl::type_list<...> of member descriptors
  constexpr auto members = get_members(type);
  // Filter out the non-readable members (not field or getters marked with the property() attribute)
  constexpr auto readableMembers =
      filter(members, [](auto member) { return is_readable(member); });

  auto invalidMemberCount = count_if(readableMembers, [&](auto member) {
    // Function-call syntax is a uniform way to get the value of a member (whether a field or a getter)
    auto&& value = member(obj);
    // Check if the NonNegative attribute is present
    if constexpr(refl::descriptor::has_attribute<NonNegative>(member)) {
      // And if so, make the necessary checks
      return value < 0;
    }
    // Recursively check the value of the member
    else if(!checkNonNegative(value)) {
      return true;
    }
    return false;
  });

  return invalidMemberCount == 0;
}

// These checks are supposed to run at compile time in the original example,
// but older compilers can't do that. So I'm just gonna make them run time for now.
constexpr Circle c1{{0., 5.}, 100.};

constexpr Circle c2{{0., 5.}, -100.};

constexpr Circle c3{{0., -5.}, 100.};

int main() {
  assert(checkNonNegative(c1));
  assert(!checkNonNegative(c2));
  assert(!checkNonNegative(c3));
  return 0;
}

#include <trompeloeil.hpp>

struct S
{
  MAKE_MOCK1(func, void(int));
};

int main() {
  S s;
  REQUIRE_CALL(s, func(3));
  s.func(3);
}

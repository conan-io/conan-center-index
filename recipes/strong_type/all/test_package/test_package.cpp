#include <strong_type/strong_type.hpp>


int main() {
  using myint = strong::type<int, struct my_int_>;

  if (value_of(myint{3}) == 3)
    return 0;

  return 1;
}

#include <tl/optional.hpp>

tl::optional<int> maybe_do_something(int i) {
  if (i < 5) {
    return i;
  } else {
    return tl::nullopt; 
  }
}

int multiply_two(int n) {
  return n * 2;
}

int main() {
  int r = maybe_do_something(0)
    .map(multiply_two)
    .map([](int n) { return n - 1; })
    .value_or(0);
  return 0;
}

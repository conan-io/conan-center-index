#include <kumi/tuple.hpp>

#include <cassert>

int main()
{
  auto t = kumi::make_tuple(1, 2.5, 'x');
  assert(kumi::size_v<decltype(t)> == 3);
  return 0;
}

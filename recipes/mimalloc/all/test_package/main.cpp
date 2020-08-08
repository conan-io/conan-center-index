#include <memory>
#include <mimalloc.h>

struct Test
{ };

int main()
{
  auto t0 = std::make_shared< Test >();

  {
    auto t1 = std::make_unique< Test >();
  }

  return 0;
}

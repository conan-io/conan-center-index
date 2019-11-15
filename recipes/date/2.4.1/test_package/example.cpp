#include <date/date.h>
#include <iostream>

int main()
{
  using namespace date;
  auto d = day{1};
  std::cout << d;
}

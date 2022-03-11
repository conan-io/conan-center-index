#include <iostream>
#include <experimental/mdspan>
#include <iomanip>

namespace stdex = std::experimental;

int main()
{
  double buffer[2 * 3 * 4] = {};
  auto s1 = stdex::mdspan<double, 2, 3, 4>(buffer);
  s1(1, 1, 1) = 42;
  auto sub1 = stdex::subspan(s1, 1, 1, stdex::all);
  std::cout << std::boolalpha << (sub1[1] == 42) << std::endl;
}

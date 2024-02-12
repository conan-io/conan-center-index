#include <iostream>
#include <iomanip>
#include <experimental/mdspan>

namespace stdex = std::experimental;

int main()
{
  double buffer[2 * 3 * 4] = {};
#ifdef MDSPAN_ENABLE_SUBMDSPAN
  auto s1 = stdex::mdspan<double, stdex::dextents<size_t, 3>>(buffer, 2, 3, 4);
#else
  auto s1 = stdex::mdspan<double, 2, 3, 4>(buffer);
#endif
  s1(1, 1, 1) = 42;

#ifdef MDSPAN_ENABLE_SUBMDSPAN
  auto sub1 = stdex::submdspan(s1, 1, 1, stdex::full_extent);
#else
  auto sub1 = stdex::subspan(s1, 1, 1, stdex::all);
#endif
  std::cout << std::boolalpha << (sub1[1] == 42) << std::endl;
}

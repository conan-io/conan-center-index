#include <svgpp/svgpp.hpp>
#include <algorithm>
#include <iterator>

using namespace svgpp;

struct Context
{
  void transform_matrix(const boost::array<double, 6> & matrix)
  {
    std::copy(matrix.begin(), matrix.end(), 
      std::ostream_iterator<double>(std::cout, " "));
    std::cout << "\n";
  }
};

int main()
{
  Context context;
  value_parser<tag::type::transform_list>::parse(tag::attribute::transform(), context,
    std::string("translate(-10,-20) scale(2) rotate(45) translate(5,10)"), tag::source::attribute());
  return 0;
}

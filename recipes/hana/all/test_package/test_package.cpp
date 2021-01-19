#include <iostream>

#include <boost/hana.hpp>

int main(void)
{
  using namespace boost;
  auto map = hana::make_map(
    hana::make_pair(hana::type_c<char>,   "char"),
    hana::make_pair(hana::type_c<int>,    "int"),
    hana::make_pair(hana::type_c<long>,   "long"),
    hana::make_pair(hana::type_c<float>,  "float"),
    hana::make_pair(hana::type_c<double>, "double")
  );
}

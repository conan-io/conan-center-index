#include <pdal/pdal_config.hpp>
#include <iostream>

int main()
{
  std::cout << pdal::Config::fullVersionString() << std::endl;
  std::cout << pdal::Config::debugInformation() << std::endl;

  return 0;
}

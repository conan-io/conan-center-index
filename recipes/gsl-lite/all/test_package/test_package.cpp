#include <iostream>
#include <gsl/gsl-lite.hpp>

int main()
{
  char const s[] = "Hello, World!";
  gsl::span<char const> sp(s) ;
  std::cout << sp << std::endl;
}

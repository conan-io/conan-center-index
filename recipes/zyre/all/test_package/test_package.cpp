#include <iostream>
#include <zyre.h>

int main(void)
{
  uint64_t version = zyre_version();

  std::cout << "zyre version : " << version << std::endl; 

  return 0;
}

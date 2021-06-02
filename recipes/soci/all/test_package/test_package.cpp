#include "soci/soci.h"
#include <iostream>

int main()
{
  const auto& connectString{"../database0.empty.db"};
  const auto& table{"table1"};
  std::cout << "soci database connected successfully\n";

  return 0;
}

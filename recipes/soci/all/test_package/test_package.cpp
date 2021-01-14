//#include "soci/soci.h"
//#include "soci/empty/soci-empty.h"
#include <iostream>

int main()
{
  const auto& connectString{"../database0.empty.db"};
  const auto& table{"table1"};
//  const soci::backend_factory& backEnd = soci::empty;
  std::cout << "soci empty test\n";

  return 0;
}

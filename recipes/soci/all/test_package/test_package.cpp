#include "soci/soci.h"
//#include "soci/empty/soci-empty.h"
#include <iostream>

int main()
{
  const auto& connectString{"../database0.empty.db"};
  const auto& table{"table1"};
//  const soci::backend_factory& backEnd = *soci::factory_empty();
//  soci::session sql(backEnd, connectString);
  std::cout << "soci database connected successfully\n";

  return 0;
}

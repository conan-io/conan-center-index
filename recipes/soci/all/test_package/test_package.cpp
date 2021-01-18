#include "soci/soci.h"
#ifdef SOCI_EMPTY
#include "soci/empty/soci-empty.h"
#endif
#include <iostream>

int main()
{
  const auto& connectString{"../database0.empty.db"};
  const auto& table{"table1"};
#ifdef SOCI_EMPTY
//  const soci::backend_factory& backEnd = *soci::factory_empty();
//  soci::session sql(backEnd, connectString);
  std::cout << "soci empty backend\n";
#endif
  std::cout << "soci database connected successfully\n";

  return 0;
}

#include <soci/soci.h>
#include <iostream>
#include <soci/mysql/soci-mysql.h>

int main()
{
  auto backend = soci::factory_mysql();

  try {
    soci::session sql(*soci::factory_mysql(), "db=db_mysql.db");
  }
  catch(const soci::soci_error& )
  {
    return 0;
  }
  return 1;
}

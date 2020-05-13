#include <soci/soci.h>
#include <iostream>
#include <soci/odbc/soci-odbc.h>

int main()
{
  auto backend = soci::factory_odbc();

  try {
    soci::session sql(*soci::factory_odbc(), "db=db_odbc.db");
  }
  catch(const soci::soci_error& )
  {
    return 0;
  }
  return 1;
}

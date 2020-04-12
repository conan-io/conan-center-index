#include <soci/soci.h>
#include <iostream>
#include <soci/postgresql/soci-postgresql.h>

int main()
{
  try {
    soci::session sql(*soci::factory_postgresql(), "db=test.db");
  }
  catch(const soci::soci_error& )
  {
    return 0;
  }
  return 1;
}

#include "catch2/catch.hpp"
#include "soci/soci.h"
#include "soci/empty/soci-empty.h"
#include <string>

const auto& connectString{"../database0.empty.db"};
const auto& table{"table1"};
const soci::backend_factory& backEnd = *soci::factory_empty();
soci::session sql(backEnd, connectString);

TEST_CASE("should be connected")
{
  CHECK( sql.is_connected() ); //! Since soci 4.0.1
}

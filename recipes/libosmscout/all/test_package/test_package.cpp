#define M_PI 3.1415926
#include <osmscout/Database.h>
#include <osmscout/MapService.h>

int main(int argc, char** argv)
{
  osmscout::DatabaseParameter databaseParameter;
  osmscout::DatabaseRef database = std::make_shared<osmscout::Database>(databaseParameter);
  osmscout::MapServiceRef mapService = std::make_shared<osmscout::MapService>(database);
  return 0;
}


#include "leveldb/db.h"
#include <iostream>

int main()
{
  leveldb::DB *db;
  leveldb::Options options;
  options.create_if_missing = true;
  leveldb::Status status = leveldb::DB::Open(options, "testdb", &db);

  if (status.ok())
  {
    std::cout << "ok" << std::endl;
  }
  else
  {
    std::cout << "not ok" << std::endl;
  }
  return 0;
}

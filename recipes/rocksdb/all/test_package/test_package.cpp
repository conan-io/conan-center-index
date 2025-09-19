#include <cstdlib>
#include <iostream>
#include "rocksdb/db.h"


int main() {
  std::cout << "RocksDB version: " << rocksdb::GetRocksVersionAsString() << std::endl;
  return EXIT_SUCCESS;
}

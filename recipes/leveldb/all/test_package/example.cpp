#include <iostream>

#include "leveldb/db.h"
#include "leveldb/write_batch.h"

int main() {
  leveldb::DB* db;
  leveldb::Options options;
  options.create_if_missing = true;
  options.error_if_exists = false;
  auto status = leveldb::DB::Open(options, "temp_db", &db);
  if (!status.ok()) {
    std::cerr << "Failed to open temp_db"  << std::endl;
    return EXIT_FAILURE;
  }

  db->Put(leveldb::WriteOptions(), "key1", "value1");
  std::string value;
  db->Get(leveldb::ReadOptions(), "key1", &value);
  db->Put(leveldb::WriteOptions(), "key2", "value1");

  leveldb::WriteBatch batch;
  batch.Delete("key1");
  batch.Delete("key2");

  db->Write(leveldb::WriteOptions(), &batch);

  delete db;

  return 0;
}


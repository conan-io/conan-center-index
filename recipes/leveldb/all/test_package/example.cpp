#include <cstdlib>
#include <filesystem>
#include <iostream>

#include "leveldb/db.h"
#include "leveldb/write_batch.h"

namespace {

void exit_if_failed(leveldb::Status status, const leveldb::DB *db) {
  if (!status.ok()) {
    std::cerr << "Error due to leveldb status " << status.ToString() << std::endl;
    if (db) {
      delete db;
    }
    std::exit(EXIT_FAILURE);
  }
}

}

int main() {
  auto tmpdb_path = std::filesystem::temp_directory_path() / "conanleveldbtest";

  leveldb::DB* db;
  leveldb::Options options;
  options.create_if_missing = true;
  options.error_if_exists = true;
  leveldb::Status status = leveldb::DB::Open(options, tmpdb_path, &db);

  exit_if_failed(status, db); status = db->Put(leveldb::WriteOptions(), "key1", "value1");
  std::string value;
  exit_if_failed(status, db); status = db->Get(leveldb::ReadOptions(), "key1", &value);
  exit_if_failed(status, db); status = db->Put(leveldb::WriteOptions(), "key2", "value1");

  leveldb::WriteBatch batch;
  batch.Delete("key1");
  batch.Delete("key2");

  exit_if_failed(status, db); status = db->Write(leveldb::WriteOptions(), &batch);
  exit_if_failed(status, db); delete db;

  std::filesystem::remove_all(tmpdb_path);

  return 0;
}


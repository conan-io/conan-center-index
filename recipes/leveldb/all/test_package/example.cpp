#include <filesystem>
#include <iostream>
#include <random>

#include "leveldb/db.h"
#include "leveldb/write_batch.h"

#include "example.hpp"

using namespace conan::recipe;

ScopedTempDir::ScopedTempDir() {
  auto tmp = fs::temp_directory_path();
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_int_distribution<> dist;

  bool created = false;
  std::string prefix("tmp-conan-leveldb-");
  for (int attempt = 0; attempt < 100 && !created; attempt++) {
    auto suffix = dist(gen);
    path = tmp / (prefix + std::to_string(dist(gen)));
    if (!fs::exists(path)) {
      created = fs::create_directory(path);
    }
  }

  if (!created) {
    throw std::runtime_error("failed to create temporary directory for test");
  }

}

int main() {
  ScopedTempDir tmpdir;

  leveldb::DB* db;
  leveldb::Options options;
  options.create_if_missing = true;
  options.error_if_exists = true;
  auto status = leveldb::DB::Open(options, tmpdir.GetPath(), &db);
  if (!status.ok()) {
    std::cerr << "Failed to open tempdb at " << tmpdir.GetPath() << std::endl;
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


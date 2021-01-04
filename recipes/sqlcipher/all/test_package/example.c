#include <sqlcipher/sqlite3.h>

int main() {
  sqlite3* db;
  sqlite3_open(":memory:", &db);
  int ret = sqlite3_key(db, "toto", 5);
  sqlite3_close(db);
  return ret;
}

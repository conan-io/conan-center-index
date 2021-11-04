#include <cassandra.h>

#include <memory>
#include <string>

struct Basic_ {
  cass_bool_t bln;
  cass_float_t flt;
  cass_double_t dbl;
  cass_int32_t i32;
  cass_int64_t i64;
};
typedef struct Basic_ Basic;

int insert_into_basic(const char* key, const Basic* basic) {
  const char* query =
      "INSERT INTO examples.basic (key, bln, flt, dbl, i32, i64) VALUES (?, ?, "
      "?, ?, ?, ?);";

  auto statement =
      std::unique_ptr<CassStatement, decltype(&cass_statement_free)>(
          cass_statement_new(query, 6), &cass_statement_free);

  cass_statement_bind_string(statement.get(), 0, key);
  cass_statement_bind_bool(statement.get(), 1, basic->bln);
  cass_statement_bind_float(statement.get(), 2, basic->flt);
  cass_statement_bind_double(statement.get(), 3, basic->dbl);
  cass_statement_bind_int32(statement.get(), 4, basic->i32);
  cass_statement_bind_int64(statement.get(), 5, basic->i64);

  return 0;
}

int main(int argc, char* argv[]) {
  Basic input = {cass_true, 0.001f, 0.0002, 1, 2};

  insert_into_basic("test", &input);
  return 0;
}

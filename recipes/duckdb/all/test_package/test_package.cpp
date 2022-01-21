#include "duckdb.hpp"
#include <iostream>

int main() {
    duckdb::DuckDB db(nullptr);
    duckdb::Connection con(db);

    return 0;
}

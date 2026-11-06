#include <iostream>
#include "duckdb.hpp"

int main() {
    duckdb::DuckDB db(nullptr);
    duckdb::Connection con(db);
    // Only look at what is linked into the package, never install or load from the network
    con.Query("SET autoinstall_known_extensions=false");
    con.Query("SET autoload_known_extensions=false");

    // Fails unless core_functions and parquet are statically linked and registered
    auto result = con.Query("SELECT string_agg(extension_name, ', ' ORDER BY extension_name) AS loaded, "
                            "CASE WHEN count(*) FILTER (WHERE extension_name IN ('core_functions', 'parquet')) = 2 "
                            "THEN 'ok' ELSE error('core_functions or parquet is not statically loaded') END AS status "
                            "FROM duckdb_extensions() WHERE loaded");
    std::cout << result->ToString() << std::endl;
    return result->HasError() ? 1 : 0;
}

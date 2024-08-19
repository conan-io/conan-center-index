#include <iostream>

#include <mysqlx/xdevapi.h>


int main() {
    mysqlx::Session sess("mysqlx://root@127.0.0.1");
    mysqlx::RowResult res = sess.sql("show variables like 'version'").execute();
    std::stringstream version;
    version << res.fetchOne().get(1).get<std::string>();
    std::cout << "mysqlx version: " << version << std::endl;
    return EXIT_SUCCESS;
}

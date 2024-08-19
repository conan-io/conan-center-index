#include <iostream>

#include <mysqlx/xdevapi.h>


int main() {
    Session sess("mysqlx://root@127.0.0.1");
    RowResult res = sess.sql("show variables like 'version'").execute();
    version << res.fetchOne().get(1).get<std::string>();
    std::cout << "mysqlx version: " << version << std::endl;
    return EXIT_SUCCESS;
}

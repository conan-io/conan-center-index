#include <iostream>

#include <mysqlx/xdevapi.h>


int main() {
    mysqlx::Session sess("mysqlx://root@127.0.0.1");
    mysqlx::RowResult res = sess.sql("show variables like 'version'").execute();
    std::stringstream version;
    version << res.fetchOne().get(1).get<std::string>();
    int major_version;
    version >> major_version;
    std::cout << "mysqlx version: " << major_version << std::endl;
    return EXIT_SUCCESS;
}

#include <mysqlx/xdevapi.h>

int main()
{
    mysqlx::SessionSettings from_url("mysqlx://user:pwd@127.0.0.1:1234/db?ssl-mode=required");
    return 0;
}

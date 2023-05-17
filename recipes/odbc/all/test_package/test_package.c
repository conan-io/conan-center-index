#include <sql.h>
#include <sqlext.h>

#include <stdio.h>

int main() {
    printf("Type of SQL_CHAR is %i\n", SQL_CHAR);
    return 0;
}

SQLRETURN driver_connect() {
    SQLHDBC dbc;
    SQLCHAR *connect_string = (unsigned char *)"DSN=mydsn;";

    return SQLDriverConnect(dbc, NULL, connect_string, SQL_NTS,
                            NULL, 0, NULL, SQL_DRIVER_COMPLETE);
}

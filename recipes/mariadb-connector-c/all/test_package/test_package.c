#include <mysql.h>
#include <stdio.h>

// See #4530
#include <mysqld_error.h>

int main(int argc, char **argv)
{
  printf("MySQL client version: %s\n", mysql_get_client_info());
  return 0;
}

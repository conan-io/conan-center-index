#include <mysql.h>
#include <stdio.h>


int main(int argc, char **argv)
{
  printf("MySQL client version: %s\n", mysql_get_client_info());
  printf("MARIADB_PLUGINDIR: %s", MARIADB_PLUGINDIR);

  return 0;
}

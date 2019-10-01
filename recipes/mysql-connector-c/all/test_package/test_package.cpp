#include <mysql.h>
#include <iostream>

int main(int argc, char **argv)
{
  std::cout << "MySQL client version: " << mysql_get_client_info() << std::endl;
  return 0;
}

#include <iostream>

#include <libkeepass/database.hh>

int main() {
  keepass::Database db;
  std::cout << "libkeepass test_package: Database constructed and linked OK\n";
  return 0;
}

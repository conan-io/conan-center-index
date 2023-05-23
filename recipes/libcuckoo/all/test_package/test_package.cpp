#include <iostream>
#include <string>

#include <libcuckoo/cuckoohash_map.hh>

int main() {
  libcuckoo::cuckoohash_map<int, std::string> Table;

  for (int i = 0; i < 10; i++) {
    Table.insert(i, "found");
  }

  std::string out;
  for (int i = 0; i < 11; i++) {

    if (Table.find(i, out)) {
      std::cout << i << "  " << out << '\n';
    } else {
      std::cout << i << "  NOT FOUND\n";
    }
  }
}

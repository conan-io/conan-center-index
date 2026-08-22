#include <tiledb/tiledb>

#include <iostream>

int main() {
  tiledb::Context ctx;

  auto version = tiledb::version();
  std::cout << "TileDB version: "
            << std::get<0>(version) << "." << std::get<1>(version) << "." << std::get<2>(version)
            << std::endl;

  return 0;
}

#include <iostream>
#include <loon/lru.hpp>

int main() {
  // Test LRU
  loon::LRU<int, std::string> cache(3);
  cache.put(1, "hello");
  auto val = cache.get(1);
  if (val && val->get() == "hello") {
    sstd::cout << "test_package for loon: OK\n";
  }
  return 0;
}

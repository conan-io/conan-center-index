#include <iostream>
#include <loon/lru.hpp>
#include <loon/redis_list.hpp>

int main() {
  // Test LRUCache
  loon::LRUCache<int, std::string> cache(3);
  cache.put(1, "hello");
  auto val = cache.get(1);
  if (val && val->get() == "hello") {
    std::cout << "LRUCache: OK\n";
  }

  // Test RedisList
  loon::RedisList<int> list;
  list.rpush(1);
  list.rpush(2);
  if (list.size() == 2) {
    std::cout << "RedisList: OK\n";
  }

  std::cout << "test_package for loon: OK\n";
  return 0;
}

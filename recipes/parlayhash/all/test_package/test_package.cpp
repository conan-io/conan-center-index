#include <iostream>
#include <string>
#include <parlay/parallel.h>
#include "parlay_hash/unordered_map.h"

using K = std::string;
using V = unsigned long;
using map_type = parlay::parlay_unordered_map<K,V>;

int main() {
  map_type my_map(100);
  my_map.Insert("sue", 1);
  my_map.Insert("sam", 5);

  std::cout << "value before increment: " << *my_map.Find("sue") << std::endl;
  auto increment = [] (std::optional<V> v) -> V {return v.has_value() ? 1 + *v : 1;};
  my_map.Upsert("sue", increment);
  std::cout << "value after increment: " << *my_map.Find("sue") << std::endl;

  std::cout << "size before remove: " << my_map.size() << std::endl;
  my_map.Remove("sue");
  std::cout << "size after remove: " << my_map.size() << std::endl;
  return 0;
}

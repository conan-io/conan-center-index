#include <iostream>
#include <string>
#include <parlay/unordered_map.h>

using K = std::string;
using V = unsigned long;
using map_type = parlay::unordered_map<K,V>;

int main() {
  map_type my_map(100);
  my_map.insert("sue", 1);
  my_map.insert("sam", 5);

  std::cout << "value before increment: " << *my_map.find("sue") << std::endl;
  auto increment = [] (std::optional<V> v) -> V {return v.has_value() ? 1 + *v : 1;};
  my_map.upsert("sue", increment);
  std::cout << "value after increment: " << *my_map.find("sue") << std::endl;

  std::cout << "size before remove: " << my_map.size() << std::endl;
  my_map.remove("sue");
  std::cout << "size after remove: " << my_map.size() << std::endl;
}

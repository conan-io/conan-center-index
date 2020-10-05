#include <rxcpp/rx.hpp>

int main() {
  auto values = rxcpp::observable<>::range(1, 3).as_blocking();
  return 0;
}

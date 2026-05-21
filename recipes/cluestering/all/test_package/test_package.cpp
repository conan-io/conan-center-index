
#include <CLUEstering/CLUEstering.hpp>

int main() {
  // Obtain the queue, which is used for allocations and kernel launches.
  auto queue = clue::get_queue(0u);
  std::cout << "Successfully obtained the queue!" << std::endl;
}

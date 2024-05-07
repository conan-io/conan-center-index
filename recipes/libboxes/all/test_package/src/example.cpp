#include <boxes/boxes.hpp>

#include <iostream>

int main() {
  boxes::RingBuffer<int, 8> buf;
  buf.push_back(123);

  if (buf.size() == 1 && buf.front() == 123) {
    std::cout << "libboxes::RingBuffer works!" << std::endl;
  } else {
    std::cout << "libboxes::RingBuffer is broken!" << std::endl;
  }

  return 0;
}

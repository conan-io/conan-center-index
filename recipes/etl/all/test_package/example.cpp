#include <etl/array.h>

int main() {
  const etl::array<int, 10> data = { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 };
  return (data.size() == 10)?0:1;
}

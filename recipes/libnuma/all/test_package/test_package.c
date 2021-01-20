#include <numa.h>

int main() {
  printf("numa available: %d\n", numa_available());
  return 0;
}

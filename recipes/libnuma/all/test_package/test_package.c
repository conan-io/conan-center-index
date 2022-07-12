#include <numa.h>
#include <stdio.h>

int main() {
  printf("numa available: %d\n", numa_available());
  return 0;
}

#include <sofa.h>

#include <stdio.h>

int main() {
  double epb = iauEpb(2415019.8135, 30103.18648);
  printf("%f\n", epb);

  return 0;
}

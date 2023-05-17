#include <poly2tri/poly2tri.h>

int main() {
  p2t::Point p1(0.0, 0.0);
  p2t::Point p2(1.0, 0.0);
  p2t::Point p3(0.0, 1.0);

  p2t::Triangle triangle(p1, p2, p3);

  return 0;
}

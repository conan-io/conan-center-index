// compile an expression and run it: the least a hobbes package has to be able to do
#include <hobbes/hobbes.H>

#include <iostream>

int main() {
  hobbes::cc c;
  const int r = c.compileFn<int()>("sum([i * i | i <- [1..10]])")();
  std::cout << "hobbes says the squares of 1..10 sum to " << r << std::endl;
  return r == 385 ? 0 : 1;
}

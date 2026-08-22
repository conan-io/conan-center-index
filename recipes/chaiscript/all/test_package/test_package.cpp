#include <chaiscript/chaiscript.hpp>
#include <iostream>
#include <cassert>

double chai_add(double i, double j)
{
  return i + j;
}

int main()
{
  chaiscript::ChaiScript chai;
  chai.add(chaiscript::fun(&chai_add), "add");
  const auto answer = chai.eval<double>("add(38.8, 3.2);");
  assert(static_cast<int>(answer) == 42);
  std::cout << "The answer is: " << answer << '\n';
}

#include <orc/OrcFile.hh>
#include <iostream>

int main() {
  auto orcType = orc::Type::buildTypeFromString("struct<a:int,b:string>");
  std::cout << orcType->toString() << std::endl;
  return 0;
}

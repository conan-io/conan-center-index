#include <iostream>
#include <pathie/path.hpp>

static bool callback(const Pathie::Path& entry)
{
  std::cout << entry << std::endl;
  return true;
}

int main()
{
  Pathie::Path dir(".");
  dir.find(callback);

  return 0;
}

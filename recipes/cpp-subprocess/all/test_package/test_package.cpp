#include <subprocess.hpp>

int main() {
  using namespace subprocess;
#ifdef _WIN32
  auto cmd = Popen({"tasklist"}, shell{false});
#else
  auto cmd = Popen({"echo", "a"}, shell{false});
#endif

  cmd.wait();

  return 0;
}

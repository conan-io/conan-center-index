#include <reproc++/run.hpp>

#include <array>
#include <string>

int main()
{
  std::array<std::string, 2> command = { "echo", "Hello, World!" };
  reproc::options options;
  options.redirect.parent = true;
  options.deadline = reproc::milliseconds(1000);
  reproc::run(command, options);
}

#include <reproc/run.h>

int main()
{
  const char *const command[] = { "echo", "Hello, World!", NULL };
  reproc_run(command, (reproc_options){ .deadline = 1000 });
}

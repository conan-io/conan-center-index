#include <stddef.h>
#include <X11/xpm.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  XpmFree(NULL);

  return 0;
}

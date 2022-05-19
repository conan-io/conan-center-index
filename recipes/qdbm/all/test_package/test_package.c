#include <qdbm/cabin.h>
#include <stddef.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  cbfree(NULL);

  return 0;
}

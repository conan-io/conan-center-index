#include <hunspell/hunspell.h>
#include <stddef.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  Hunspell_destroy(NULL);

  return 0;
}

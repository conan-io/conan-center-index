#include <editline/readline.h>
#include <stddef.h>

int main(int argc, char const* argv[])
{
  (void)argc;
  (void)argv;

  free_history_entry(NULL);

  return 0;
}

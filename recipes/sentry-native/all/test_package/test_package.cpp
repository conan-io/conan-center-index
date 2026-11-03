#include <stdlib.h>
#include "sentry.h"

int main(int argc, char **argv)
{
  sentry_options_t *options = sentry_options_new();
  sentry_options_set_release(options, "test-example-release");
  if (argc > 1) {
    sentry_options_set_database_path(options, argv[1]);
  }
  if (argc > 2) {
    // crashpad_handler or sentry-crash from the package, started by sentry_init()
    sentry_options_set_handler_path(options, argv[2]);
  }
  if (sentry_init(options) != 0) {
    return EXIT_FAILURE;
  }
  sentry_close();
  return EXIT_SUCCESS;
}

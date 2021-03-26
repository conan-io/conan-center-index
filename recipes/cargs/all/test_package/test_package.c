#include <cargs.h>
#include <stdbool.h>
#include <stdlib.h>

static struct cag_option options[] = {{.identifier = 's',
                                       .access_letters = "s",
                                       .access_name = NULL,
                                       .value_name = NULL,
                                       .description = "Simple flag"}};

int main(int argc, char *argv[]) {
  cag_option_context context;
  cag_option_prepare(&context, options, CAG_ARRAY_SIZE(options), argc, argv);

  return EXIT_SUCCESS;
}

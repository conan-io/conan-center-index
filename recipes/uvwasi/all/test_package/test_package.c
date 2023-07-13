#include <stdlib.h>
#include <assert.h>
#include "uvwasi/uvwasi.h"

int main(void) {
  uvwasi_t uvwasi;
  uvwasi_options_t init_options;
  uvwasi_errno_t err;

  /* Setup the initialization options. */
  init_options.in = 0;
  init_options.out = 1;
  init_options.err = 2;
  init_options.fd_table_size = 3;
  init_options.argc = 3;
  init_options.argv = calloc(3, sizeof(char*));
  init_options.argv[0] = "--foo=bar";
  init_options.argv[1] = "-baz";
  init_options.argv[2] = "100";
  init_options.envp = NULL;
  init_options.preopenc = 1;
  init_options.preopens = calloc(1, sizeof(uvwasi_preopen_t));
  init_options.preopens[0].mapped_path = "/var";
  init_options.preopens[0].real_path = ".";
  init_options.allocator = NULL;

  /* Initialize the sandbox. */
  err = uvwasi_init(&uvwasi, &init_options);
  assert(err == UVWASI_ESUCCESS);

  /* Clean up resources. */
  uvwasi_destroy(&uvwasi);
  return 0;
}

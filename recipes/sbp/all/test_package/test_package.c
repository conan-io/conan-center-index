#include <stdio.h>
#include <string.h>

#include <libsbp/sbp.h>
#include <libsbp/version.h>

int main(void) {
  fprintf(stderr, "Compiled with sbp %s.\n", SBP_VERSION);

  sbp_state_t s;
  sbp_state_init(&s);

  return 0;
}

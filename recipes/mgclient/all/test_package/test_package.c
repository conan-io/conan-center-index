#include <stdio.h>
#include <stdlib.h>

#include "mgclient.h"

int main(int argc, char *argv[]) {
  mg_init();
  printf("mgclient version: %s\n", mg_client_version());

  mg_session_params *params = mg_session_params_make();
  if (!params) {
    fprintf(stderr, "failed to allocate session parameters\n");
    exit(1);
  }
  mg_session_params_set_host(params, "localhsot");
  mg_session_params_set_port(params, 8888);
  mg_session_params_set_sslmode(params, MG_SSLMODE_DISABLE);

  mg_finalize();

  return 0;
}

#include <mbus/mbus.h>
#include <stdio.h>
#include <string.h>

int main() {
  mbus_handle *handle;
  char *host = "localhost";
  long port = 8000;

  if ((handle = mbus_context_tcp(host, port)) == NULL) {
    fprintf(stderr, "Scan failed: Could not initialize M-Bus context: %s\n",
            mbus_error_str());
    return 0;
  }

  mbus_context_free(handle);

  return 0;
}

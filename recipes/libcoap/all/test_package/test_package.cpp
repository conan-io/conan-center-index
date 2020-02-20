#include "coap2/coap.h"

int main(int argc, char *argv[]) {
  coap_startup();

  // create CoAP context and a client session
  coap_context_t *ctx = coap_new_context(nullptr);

  coap_free_context(ctx);
  coap_cleanup();

  return 0;
}

#include "coap2/coap.h"
#include <iostream>

int main() {
  std::cout << "starting" << std::endl;
  coap_startup();

  // create CoAP context and a client session
  coap_context_t *ctx = coap_new_context(nullptr);

  coap_free_context(ctx);
  coap_cleanup();
  std::cout << "stopping" << std::endl;
  return 0;
}

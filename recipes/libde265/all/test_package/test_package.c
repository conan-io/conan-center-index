#include <libde265/de265.h>

int main() {
  de265_decoder_context *ctx = de265_new_decoder();
  de265_free_decoder(ctx);
  return 0;
}

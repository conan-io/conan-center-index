#include <openssl/base.h>
#include <openssl/crypto.h>
#include <openssl/ssl.h>

#include <cassert>
#include <cstring>
#include <iostream>

int main() {
#if !defined(OPENSSL_IS_BORINGSSL)
#error                                                                         \
    "This test must be compiled against BoringSSL headers (OPENSSL_IS_BORINGSSL not defined)."
#endif

  // Runtime verification that we linked against BoringSSL.
  const char *version = OpenSSL_version(OPENSSL_VERSION);
  std::cout << "OpenSSL_version: " << version << "\n";
  if (!version || std::strstr(version, "BoringSSL") == nullptr) {
    std::cerr << "ERROR: The loaded libcrypto/libssl does not appear to be "
                 "BoringSSL.\n";
    return 1;
  }

  // Basic sanity to ensure libssl is usable.
  SSL_CTX *ctx = SSL_CTX_new(TLS_method());
  assert(ctx != nullptr);
  SSL_CTX_free(ctx);

  std::cout << "BoringSSL test executable linked and ran.\n";
  return 0;
}

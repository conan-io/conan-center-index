#include "gcrypt.h"

int main() {
  gcry_md_hd_t handle;
  gcry_error_t result = gcry_md_open(&handle, 0, GCRY_MD_FLAG_HMAC);
  if (result) {
      return result;
  }
  return 0;
}

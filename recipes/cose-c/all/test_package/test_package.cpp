#include <cose/cose.h>
#include <stdio.h>

#if defined(COSE_C_USE_OPENSSL)
#include <openssl/opensslv.h>
#endif

#if defined(COSE_C_USE_MBEDTLS)
#include <mbedtls/config.h>
#endif

int main(int argc, char *argv[])
{
  const int aCoseInitFlags = COSE_INIT_FLAGS_NONE;

  const auto mSign =
      COSE_Sign0_Init(static_cast<COSE_INIT_FLAGS>(aCoseInitFlags), nullptr);

  return 0;
}

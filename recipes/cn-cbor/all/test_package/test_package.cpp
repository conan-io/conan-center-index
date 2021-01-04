#include "cn-cbor/cn-cbor.h"
#include <stdio.h>

#ifdef USE_CBOR_CONTEXT
#define CBOR_CONTEXT_PARAM , NULL
#else
#define CBOR_CONTEXT_PARAM
#endif

int main(int argc, char *argv[]) {

  struct cn_cbor_errback back;
  const char *buf = "asdf";
  const int len = 4;
  const cn_cbor *ret = cn_cbor_decode((const uint8_t *)buf, len CBOR_CONTEXT_PARAM, &back);
  if (ret) {
    printf("oops 1");
  }

  return 0;
}

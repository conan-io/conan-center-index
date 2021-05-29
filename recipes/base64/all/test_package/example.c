#include <stdio.h>
#include <string.h>
#include <libbase64.h>

int main() {
  int flags = 0;
  const char * src = "YW55IGNhcm5hbCBwbGVhc3VyZQ==";
  char enc[128], dec[128];
  size_t srclen = strlen(src);
  size_t enclen, declen;

  base64_decode(src, srclen, enc, &enclen, flags);
  enc[enclen] = '\0';
  printf("decoded size (\"any carnal pleasure\"): %zu\n", enclen);
  base64_encode(enc, enclen, dec, &declen, flags);
  dec[declen] = '\0';
  printf("%s\n", dec);
  return 0;
}


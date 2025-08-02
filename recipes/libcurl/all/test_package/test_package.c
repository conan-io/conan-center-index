#include <stdio.h>
#include <curl/curl.h>

int main(void)
{
  printf("libcurl version %s\n", curl_version());
  return 0;
}

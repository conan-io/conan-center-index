#include <stdio.h>
#include <curl/curl.h>

int main(void)
{
  CURL *curl;
  int retval = 0;
  const char *const *proto;
  curl_version_info_data* id = curl_version_info(CURLVERSION_NOW);
  if (!id)
    return 1;

  printf("protocols: ");
  for(proto = id->protocols; *proto; proto++) {
    printf("%s ", *proto);
  }
  printf("\nversion: %s\nssl version: %s\nfeatures: %d\n", id->version, id->ssl_version, id->features);

  curl = curl_easy_init();
  if(curl) {
    char errbuf[CURL_ERROR_SIZE];

    /* provide a buffer to store errors in */
    curl_easy_setopt(curl, CURLOPT_ERRORBUFFER, errbuf);

    /* always cleanup */ 
    curl_easy_cleanup(curl);
    printf("Succeed\n");
  } else {
    printf("Failed to init curl\n");
    retval = 3;
  }

  return retval;
}

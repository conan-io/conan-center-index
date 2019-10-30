/* This is simple demonstration of how to use expat. This program
   reads an XML document from standard input and writes a line with
   the name of each element to standard output indenting child
   elements by one tab stop more than their parent element.
   It must be used with Expat compiled for UTF-8 output.
*/

#include <stdlib.h>
#include <stdio.h>
#include <oauth.h>


int main(int argc, char *argv[])
{
  char const * const url = "http://host.net/resource" "?" "name=value&name=value"
                           "&oauth_nonce=fake&&oauth_timestamp=1";
  OAuthMethod method = OA_PLAINTEXT;
  const char *c_key = "abcd";
  const char *c_secret = "&";
  const char *t_key = "1234";
  const char *t_secret = "&";
  //const char *expected

  int rv=0;
  char *geturl = NULL;
  geturl = oauth_sign_url2(url, NULL, method, NULL, c_key, c_secret, t_key, t_secret);
  printf("GET: URL:%s\n", geturl);
  if(geturl) free(geturl);
}

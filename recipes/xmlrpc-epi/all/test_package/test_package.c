#include <xmlrpc-epi/xmlrpc.h>

int main(int argc, char **argv)
{
  XMLRPC_SERVER server;
  server = XMLRPC_ServerCreate();
  XMLRPC_ServerDestroy(server);
  return 0;
}

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/library/snmp_api.h>
#include <net-snmp/net-snmp-includes.h>
#include <stddef.h>

int main()
{
  netsnmp_free(NULL);
  return 0;
}

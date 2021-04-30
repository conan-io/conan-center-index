#include <stdio.h>

void __collier_init_MOD_getversionnumber_cll(char[5]);

int main()
{
   char version[6];
   __collier_init_MOD_getversionnumber_cll(version);
   version[5] = '\0';

   printf("COLLIER (version %s)\n", version);

   return 0;
}

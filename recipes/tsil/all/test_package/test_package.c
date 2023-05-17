#include <stdio.h>
#include "tsil.h"

int main()
{
   TSIL_DATA data;
   TSIL_REAL x = 1.0, y = 2.0, z = 3.0, u = 4.0, v = 5.0, s = 6.0, qq = 7.0;

   TSIL_SetParameters(&data, x, y, z, u, v, qq);
   TSIL_Evaluate(&data, s);

   printf("TSIL %s\n", TSIL_VERSION);
   printf("TSIL_REAL = %i bytes\n", sizeof(TSIL_REAL));
   printf("TSIL_COMPLEXCPP =  %i bytes\n", sizeof(TSIL_COMPLEX));

   return 0;
}

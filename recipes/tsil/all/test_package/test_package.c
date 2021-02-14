#include <stdio.h>
#include "tsil.h"

int main()
{
   TSIL_DATA data;
   TSIL_REAL x = 1.0, y = 2.0, z = 3.0, u = 4.0, v = 5.0, s = 6.0, qq = 7.0;

   TSIL_SetParameters(&data, x, y, z, u, v, qq);
   TSIL_Evaluate(&data, s);

   TSIL_COMPLEX M     = TSIL_GetFunction(&data, "M");
   TSIL_COMPLEX Uzxyv = TSIL_GetFunction(&data, "Uzxyv");
   TSIL_COMPLEX Uuyxv = TSIL_GetFunction(&data, "Uuyxv");
   TSIL_COMPLEX Uxzuv = TSIL_GetFunction(&data, "Uxzuv");
   TSIL_COMPLEX Uyuzv = TSIL_GetFunction(&data, "Uyuzv");
   TSIL_COMPLEX Tvyz  = TSIL_GetFunction(&data, "Tvyz");
   TSIL_COMPLEX Tuxv  = TSIL_GetFunction(&data, "Tuxv");
   TSIL_COMPLEX Tyzv  = TSIL_GetFunction(&data, "Tyzv");
   TSIL_COMPLEX Txuv  = TSIL_GetFunction(&data, "Txuv");
   TSIL_COMPLEX Tzyv  = TSIL_GetFunction(&data, "Tzyv");
   TSIL_COMPLEX Tvxu  = TSIL_GetFunction(&data, "Tvxu");
   TSIL_COMPLEX Svyz  = TSIL_GetFunction(&data, "Svyz");
   TSIL_COMPLEX Suxv  = TSIL_GetFunction(&data, "Suxv");

   printf("=========\n");
   printf("TSIL %s\n", TSIL_VERSION);
   printf("=========\n");
   printf("TSIL_REAL = %i bytes\n", sizeof(TSIL_REAL));
   printf("TSIL_COMPLEXCPP =  %i bytes\n", sizeof(TSIL_COMPLEX));

   printf("M     = %g + i*%g\n", creal(M    ), cimag(M    ));
   printf("Uzxyv = %g + i*%g\n", creal(Uzxyv), cimag(Uzxyv));
   printf("Uuyxv = %g + i*%g\n", creal(Uuyxv), cimag(Uuyxv));
   printf("Uxzuv = %g + i*%g\n", creal(Uxzuv), cimag(Uxzuv));
   printf("Uyuzv = %g + i*%g\n", creal(Uyuzv), cimag(Uyuzv));
   printf("Tvyz  = %g + i*%g\n", creal(Tvyz ), cimag(Tvyz ));
   printf("Tuxv  = %g + i*%g\n", creal(Tuxv ), cimag(Tuxv ));
   printf("Tyzv  = %g + i*%g\n", creal(Tyzv ), cimag(Tyzv ));
   printf("Txuv  = %g + i*%g\n", creal(Txuv ), cimag(Txuv ));
   printf("Tzyv  = %g + i*%g\n", creal(Tzyv ), cimag(Tzyv ));
   printf("Tvxu  = %g + i*%g\n", creal(Tvxu ), cimag(Tvxu ));
   printf("Svyz  = %g + i*%g\n", creal(Svyz ), cimag(Svyz ));
   printf("Suxv  = %g + i*%g\n", creal(Suxv ), cimag(Suxv ));

   return 0;
}

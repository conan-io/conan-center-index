#include "newmatap.h"

int main()
{
   Matrix matrix(4,4);

   matrix
       <<  1 <<  2 <<  3 << 4
       <<  21 <<  22 <<  23 << 24
       <<  31 <<  32 <<  33 << 34
       <<  41 <<  42 <<  43 <<   44
       ;

   return 0;
}

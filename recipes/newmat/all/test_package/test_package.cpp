#include "newmatap.h"
#include <iostream>

int main()
{
   Matrix matrix(4,4);

   matrix
       <<  1 <<  2 <<  3 << 4
       <<  21 <<  22 <<  23 << 24
       <<  31 <<  32 <<  33 << 34
       <<  41 <<  42 <<  43 <<   44
       ;

   std::cout << matrix[0][0];
   std::cout << matrix[3][3];

   return 0;
}

#include "lib.h"

#include <stdio.h>

int main(int argc, char * argv[])
{
    double res = my_function(1.44);
    printf("Result is %e\n", res);
    printf("The secret value is %d\n", libtestlib_value);
    return 0;
}

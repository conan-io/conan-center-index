#include <stdio.h>

double my_function(double);

int main(int argc, char * argv[])
{
    double res = my_function(1.57);
    printf("Result is %e\n", res);
    return 0;
}

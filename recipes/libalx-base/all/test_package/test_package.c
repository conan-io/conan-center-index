#define ALX_NO_PREFIX
#include <alx/base/stdio.h>

#include <stdio.h>
#include <stdlib.h>


int main(void)
{
	printf_b_init();
	printf("%i == %#B\n" 5, 5);

	exit(EXIT_SUCCESS);
}

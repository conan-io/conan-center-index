#include <stdio.h>

#define CTEST_MAIN

#include "ctest.h"

int main(int argc, const char *argv[])
{
	int result = ctest_main(argc, argv);

	if (result == 0)
	{
		printf("\nNOTE: all tests passed, it works! ;)\n");
	}

	return result;
}

CTEST(suite1, test2)
{
	ASSERT_EQUAL(1, 1);
}

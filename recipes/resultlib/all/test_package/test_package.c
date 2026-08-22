#include <stdlib.h>
#include <stdio.h>
#include <resultlib/result.h>

RESULT_STRUCT_TAG(int, const char *, RESULT_TAG(int, text));

int main() {
    const RESULT(int, text) result1 = RESULT_SUCCESS(42);
    const RESULT(int, text) result2 = RESULT_FAILURE("Testing failure");

    printf("Testing Result Library\n");

    if (RESULT_HAS_FAILURE(result1)) {
      fprintf(stderr, "Error: expecting result1 to be success\n");
      return EXIT_FAILURE;
    }

    if (RESULT_HAS_SUCCESS(result2)) {
      fprintf(stderr, "Error: expecting result2 to be failure\n");
      return EXIT_FAILURE;
    }

    printf("- result1: success (%d)\n", RESULT_USE_SUCCESS(result1));
    printf("- result2: failure (%s)\n", RESULT_USE_FAILURE(result2));

    return EXIT_SUCCESS;
}

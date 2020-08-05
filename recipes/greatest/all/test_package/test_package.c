#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

#include "greatest.h"

TEST standalone_test(void) {
    ASSERT(1>0);
}


/* Add all the definitions that need to be in the test runner's main file. */
GREATEST_MAIN_DEFS();

int main(int argc, char **argv) {
    GREATEST_MAIN_BEGIN();      /* command-line arguments, initialization. */
    RUN_TEST(standalone_test);

    GREATEST_MAIN_END();        /* display results */
}


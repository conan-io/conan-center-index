#include "tre/tre.h"
#include <stdio.h>

int main()
{
    regex_t rx;
    tre_regcomp(&rx, "(January|February)", REG_EXTENDED);

    regaparams_t params = {0};
    tre_regaparams_default(&params);

    regamatch_t match = {0};

    if (!tre_regaexec(&rx, "Janvary", &match, params, 0)) {
        printf("Levenshtein distance: %d\n", match.cost);
    } else {
        printf("Failed to match\n");
    }

    return 0;
}

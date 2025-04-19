#include "cargs.h"
#include <stdio.h>

CARGS_OPTIONS(
    options,
    HELP_OPTION(FLAGS(FLAG_EXIT)),
    OPTION_FLAG('v', "verbose", HELP("Enable verbose mode")),
    OPTION_STRING('o', "output", HELP("Output file"), DEFAULT("output.txt"))
)

int main(int argc, char **argv)
{
    cargs_t cargs = cargs_init(options, "test_package", "1.0.0");
    
    int status = cargs_parse(&cargs, argc, argv);
    if (status != CARGS_SUCCESS) {
        return status;
    }
    
    bool verbose = cargs_get(cargs, "verbose").as_bool;
    const char *output = cargs_get(cargs, "output").as_string;
    
    printf("Test package ran successfully!\n");
    printf("  Verbose: %s\n", verbose ? "yes" : "no");
    printf("  Output: %s\n", output);
    
    cargs_free(&cargs);
    return 0;
}

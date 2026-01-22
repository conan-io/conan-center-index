#include "argus.h"
#include <stdio.h>

ARGUS_OPTIONS(
    options,
    HELP_OPTION(),
    OPTION_FLAG('v', "verbose", HELP("Enable verbose mode")),
    OPTION_STRING('o', "output", HELP("Output file"), DEFAULT("output.txt")),
)

int main(int argc, char **argv)
{
    argus_t argus = argus_init(options, "test_package", "1.0.0");
    
    int status = argus_parse(&argus, argc, argv);
    if (status != ARGUS_SUCCESS) {
        return status;
    }
    
    bool verbose = argus_get(&argus, "verbose").as_bool;
    const char *output = argus_get(&argus, "output").as_string;

    printf("Test package ran successfully!\n");
    printf("  Verbose: %s\n", verbose ? "yes" : "no");
    printf("  Output: %s\n", output);
    
    argus_free(&argus);
    return 0;
}

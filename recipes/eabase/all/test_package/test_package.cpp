#include <eabase.h>

#include <cstdlib>
#include <iostream>

#ifndef EA_COMPILER_IS_ANSIC
#define EA_COMPILER_IS_ANSIC 0
#endif
#ifndef EA_COMPILER_IS_C99
#define EA_COMPILER_IS_C99 0
#endif
#ifndef EA_COMPILER_IS_C99
#define EA_COMPILER_IS_C99 0
#endif
#ifndef EA_COMPILER_HAS_C99_TYPES
#define EA_COMPILER_HAS_C99_TYPES 0
#endif
#ifndef EA_COMPILER_IS_CPLUSPLUS
#define EA_COMPILER_IS_CPLUSPLUS 0
#endif

int main() {
#define PRINT_COMPILER_INFO(VAR) std::cout << #VAR << ": " << (VAR) << '\n'

    PRINT_COMPILER_INFO(EA_COMPILER_VERSION);
    PRINT_COMPILER_INFO(EA_COMPILER_NAME);
    PRINT_COMPILER_INFO(EA_COMPILER_STRING);

    std::cout << '\n';

    PRINT_COMPILER_INFO(EA_PLATFORM_NAME);
    PRINT_COMPILER_INFO(EA_PLATFORM_DESCRIPTION);

    std::cout << '\n';

    PRINT_COMPILER_INFO(EA_COMPILER_IS_ANSIC);
    PRINT_COMPILER_INFO(EA_COMPILER_IS_C99);
    PRINT_COMPILER_INFO(EA_COMPILER_HAS_C99_TYPES);
    PRINT_COMPILER_INFO(EA_COMPILER_IS_CPLUSPLUS);

    std::cout << '\n';

    PRINT_COMPILER_INFO(EA_PLATFORM_PTR_SIZE);
    PRINT_COMPILER_INFO(EA_PLATFORM_WORD_SIZE);

    return EXIT_SUCCESS;
}

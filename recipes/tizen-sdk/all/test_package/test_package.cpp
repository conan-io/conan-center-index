#include <cstdlib>
#include <iostream>

#include <tizen.h>

#ifdef __cplusplus
extern "C" {
#endif

// This method is exported from library
EXPORT_API bool tizen_test(void);

#ifdef __cplusplus
}
#endif

bool tizen_test(void)
{
	return true;
}

int main()
{
    std::cout << "conan-center-index\n";
    return EXIT_SUCCESS;
}

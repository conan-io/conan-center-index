#include "lz4.h"

#ifdef _MSC_VER
#define API __declspec(dllexport)
#else
#define API __attribute__ ((visibility("default")))
#endif

API
int lz4_version()
{
    return LZ4_versionNumber();
}

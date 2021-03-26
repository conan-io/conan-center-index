#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "amd_ags.h"

int main()
{
    AGSDriverVersionResult result = agsCheckDriverVersion("18.8.2", AGS_MAKE_VERSION(18, 8, 3));
    return 0;
}

#ifdef __DXC_TEST_WINDOWS
#include <Windows.h>
#else
#include <WinAdapter.h>
#endif

#include <dxcapi.h>

int main() 
{
    // It is sufficient to check if the dxcapi.h compiled without issues on all targeted platforms
    // We will still check integrity by running dcx
    return 0;
}

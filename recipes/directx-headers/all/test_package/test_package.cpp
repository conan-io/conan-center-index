#include <wsl/winadapter.h>
#include <dxguids/dxguids.h>

int main()
{
    return sizeof(IID_IUnknown) == 0;
}

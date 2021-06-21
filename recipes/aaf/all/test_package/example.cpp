#include "AAF.h"
#include "AAFResult.h"

int main() {
    HRESULT hr = AAFLoad(nullptr);

    if (AAFRESULT_SUCCEEDED(hr)) {
        return 0;
    } else {
        return -1;
    }
}

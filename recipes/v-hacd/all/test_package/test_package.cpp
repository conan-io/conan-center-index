#define ENABLE_VHACD_IMPLEMENTATION 1
#define VHACD_DISABLE_THREADING 1
#include <VHACD.h>

int main() {
    VHACD::IVHACD *iface = VHACD::CreateVHACD();
    iface->Release();
    return 0;
}

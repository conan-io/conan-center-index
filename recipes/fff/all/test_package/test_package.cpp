#include <fff.h>

#include <cstdint>

DEFINE_FFF_GLOBALS;

FAKE_VOID_FUNC(TestFunction, uint32_t, uint8_t);

int main() {
    RESET_FAKE(TestFunction);
    FFF_RESET_HISTORY();

    TestFunction(8, 16);

    return 0;
}

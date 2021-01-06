#include <raylib.h>

int main(void) {
    InitWindow(100, 100, "basic window");
    if (IsWindowReady()) CloseWindow();
    return 0;
}

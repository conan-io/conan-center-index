#define RAYGUI_IMPLEMENTATION
#include <raygui.h>
#include <stdio.h>

int main(void) {
    GuiEnable();
    printf("Raygui version: %s\n", RAYGUI_VERSION);
    return 0;
}

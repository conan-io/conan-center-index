#include "drawille/Canvas.h"


int main() {
    Canvas* canvas = new_canvas(100, 100);

    free_canvas(canvas);

    return 0;
}

#include <ege.h>
#include <windows.h>

using namespace ege;

int main() {
    initgraph(640, 480);
    circle(120, 120, 100);
    Sleep(2000);
    closegraph();
}

#include <ege.h>
#include <windows.h>

#ifdef _MSC_VER
#pragma comment(lib,"msvcrtd.lib")
#endif

using namespace ege;

int main() {
    initgraph(640, 480);
    circle(120, 120, 100);
    Sleep(2000);
    closegraph();
}

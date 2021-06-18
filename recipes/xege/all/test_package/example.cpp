#include <ege.h>

using namespace ege;

int main() {
    initgraph(640, 480);
    circle(120, 120, 100);
    int i = 0;
    while (is_run()) {
        key_msg msg = getkey();
        if (msg.msg == key_msg_char) {
            xyprintf(0, i * 20, "%d", msg.key);
            ++i;
        }
    }
}

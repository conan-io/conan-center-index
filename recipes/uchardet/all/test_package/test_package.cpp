#include <uchardet/uchardet.h>

int main(int argc, char** argv) {
    auto ud = uchardet_new();
    uchardet_delete(ud);
    return 0;
}

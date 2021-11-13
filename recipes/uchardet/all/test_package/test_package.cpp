#include <iostream>
#include <uchardet.h>

int main(int argc, char** argv) {
    auto ud = uchardet_new();
    uchardet_delete(ud);
    LOG(INFO) << "It works";
    return 0;
}

#include <glad/gl.h>
#include <iostream>

int main() {
    gladLoadGL([] (const char *func) -> void (*)() { return nullptr; });
    return 0;
}

#include "quickjs/quickjs.h"

int main() {
    struct JSRuntime* rt = JS_NewRuntime();

    JS_FreeRuntime(rt);

    return 0;
}

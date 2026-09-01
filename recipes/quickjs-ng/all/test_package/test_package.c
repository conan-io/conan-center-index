#include "quickjs.h"

int main()
{
    JSRuntime *rt = JS_NewRuntime();
    JS_FreeRuntime(rt);
    return 0;
}

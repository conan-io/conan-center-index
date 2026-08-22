#include <mujs.h>

#include <stdio.h>

static void hello(js_State *J)
{
    const char *name = js_tostring(J, 1);
    printf("Hello, %s!\n", name);
    js_pushundefined(J);
}

int main(void)
{
    js_State *J = js_newstate(NULL, NULL, JS_STRICT);

    js_newcfunction(J, hello, "hello", 1);
    js_setglobal(J, "hello");

    js_dostring(J, "hello('world');");

    js_freestate(J);

    return 0;
}

#include "jerryscript.h"

int main()
{
    const jerry_char_t script[] = "var str = 'Hello, World!';";

    bool ret_value = jerry_run_simple(script, sizeof(script) - 1, JERRY_INIT_EMPTY);

    return (ret_value ? 0 : 1);
}

#include "lua.h"
#include "lualib.h"
#include "luacode.h"

#include <cstdlib>

int main() {
    const char source[] = "return 42";
    size_t size = 0;
    std::free(luau_compile(source, sizeof(source) - 1, nullptr, &size));
    lua_close(luaL_newstate());
    return 0;
}

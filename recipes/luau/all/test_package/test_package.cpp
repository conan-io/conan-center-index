#include "lua.h"
#include "lualib.h"
#include "luacode.h"

#include <cstdlib>
#include <string>

int main(int argc, char* argv[]) {
    lua_State* L = luaL_newstate();
    size_t size = 0;
    std::free(luau_compile("return 0", 8, nullptr, &size));
    lua_close(L);
    return 0;
}

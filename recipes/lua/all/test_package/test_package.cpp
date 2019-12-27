
#if defined COMPILE_AS_CPP
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"
#else
#include "lua.hpp"
#endif
#include <string>

int main(int argc, char* argv[])
{
    lua_State* L = luaL_newstate();
    luaL_dostring(L, "x = 47");
    lua_getglobal(L, "x");
    lua_Number x = lua_tonumber(L, 1);
    printf("lua says x = %d\n", (int)x);
    lua_close(L);
    return 0;
}

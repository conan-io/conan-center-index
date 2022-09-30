#include "lua.h"
#include "lualib.h"

#include <string>

int main(int argc, char* argv[]) {
    lua_State* L = luaL_newstate();
    lua_close(L);
    return 0;
}

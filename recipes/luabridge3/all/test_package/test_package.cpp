#include <lua.hpp>
#include <LuaBridge/LuaBridge.h>

#include <cstdlib>
#include <iostream>

int main() {
    lua_State* L = luaL_newstate();
    luaL_openlibs(L);

    luabridge::getGlobalNamespace(L)
        .addFunction("add", +[](int a, int b) { return a + b; });

    if (luaL_dostring(L, "assert(add(1, 2) == 3)") != LUA_OK) {
        std::cerr << lua_tostring(L, -1) << std::endl;
        lua_close(L);
        return EXIT_FAILURE;
    }

    lua_close(L);
    std::cout << "LuaBridge OK" << std::endl;
    return EXIT_SUCCESS;
}

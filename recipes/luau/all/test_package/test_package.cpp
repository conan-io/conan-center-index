#include "lua.h"
#include "lualib.h"
#include "luacode.h"

#include <cstdlib>
#include <cstring>

int main() {
    lua_State* L = luaL_newstate();
    luaL_openlibs(L);

    // Compiling a chunk exercises Luau.Compiler (and Luau.Bytecode, which it links since 0.718).
    const char* source = "return 6 * 7";
    size_t bytecode_size = 0;
    char* bytecode = luau_compile(source, std::strlen(source), nullptr, &bytecode_size);
    const int load_status = luau_load(L, "test", bytecode, bytecode_size, 0);
    std::free(bytecode);

    int result = 0;
    if (load_status == 0 && lua_pcall(L, 0, 1, 0) == 0) {
        result = static_cast<int>(lua_tointeger(L, -1));
    }
    lua_close(L);
    return result == 42 ? EXIT_SUCCESS : EXIT_FAILURE;
}

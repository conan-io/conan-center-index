#include "debug_assert.hpp"

//=== module A ===//
#define MODULE_A_LEVEL 1 // macro to control assertion level
// usually set by the build system

// tag type that defines a module
struct module_a : debug_assert::default_handler,          // it uses the default handler
                  debug_assert::set_level<MODULE_A_LEVEL> // and this level
{
};

int main()
{
    return 0;
    DEBUG_UNREACHABLE(module_a{});       // mark unreachable statements
}

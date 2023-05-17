#include <cstdlib>

#include <limits>

#ifdef SOL2_V3
#include <sol/sol.hpp>
#else
#include <sol.hpp>
#endif

int main() {
	sol::state lua;

	auto bob_table = lua.create_table("bob");
	bob_table.set("is_set", 42);

	int is_set = bob_table.get_or("is_set", 3);
	int is_not_set = bob_table.get_or("is_not_set", 22);

	if (is_set != 42 || is_not_set != 22) {
        return EXIT_FAILURE;
    }
	
    return EXIT_SUCCESS;
}

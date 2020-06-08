

#include <cstdlib>
#include <sol.hpp>

struct test_stack_guard {
	lua_State* L;
	int& begintop;
	int& endtop;
	test_stack_guard(lua_State* L, int& begintop, int& endtop)
		: L(L), begintop(begintop), endtop(endtop) {
		begintop = lua_gettop(L);
	}

	void check() {
		if (begintop != endtop) {
			std::abort();
		}
	}

	~test_stack_guard() {
		endtop = lua_gettop(L);
	}
};

#define REQUIRE(x) if (!(x)) throw "bad" ;
#define REQUIRE_FALSE(x) if (x) throw "bad" ;

int main() {

	sol::state lua;
	lua.open_libraries();
	lua.set_function("f", [&](bool num) {
		REQUIRE(num == true);
		return num;
	});
	auto result1 = lua.safe_script("x = f(true)\n"
		"assert(x == true)", sol::script_pass_on_error);
	REQUIRE(result1.valid());
	sol::object x = lua["x"];
	REQUIRE(x.is<bool>());
	REQUIRE(x.as<bool>() == true);
	REQUIRE_FALSE(x.is<std::int32_t>());

}
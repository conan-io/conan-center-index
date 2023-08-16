#include <cassert>
#include <string>

#include "semimap.h"

#define ID(x) \
    []() constexpr { return x; }

int main() {

    // Test compile-time only load/store
    {
        struct Tag {
        };
        using map = semi::static_map<std::string, std::string, Tag>;

        auto& food = map::get(ID("food"));
        assert(food.empty());

        food = "pizza";
        assert(map::get(ID("food")) == "pizza");

        auto& drink = map::get(ID("drink"));
        assert(drink.empty());

        drink = "beer";
        assert(map::get(ID("food")) == "pizza");
        assert(map::get(ID("drink")) == "beer");

        map::get(ID("food")) = "spaghetti";
        assert(map::get(ID("food")) == "spaghetti");
        assert(map::get(ID("drink")) == "beer");

        map::get(ID("drink")) = "soda";
        assert(map::get(ID("food")) == "spaghetti");
        assert(map::get(ID("drink")) == "soda");

        assert(map::get(ID("starter"), "soup") == "soup");
        assert(map::get(ID("starter"), "salad") == "soup");
    }

    return 0;
}

#include <cassert>
#include <list>

#include <sparrow/builder/builder.hpp>

int main([[maybe_unused]] int argc, [[maybe_unused]] char** argv)
{
    // using initializer_list
    auto arr = sparrow::build({1, 2, 3, 4, 5});
    /////////////////////
    // using vector
    std::vector<int> v{1, 2, 3, 4, 5};
    auto arr2 = sparrow::build(v);
    /////////////////////
    // using list
    std::list<int> l{1, 2, 3, 4, 5};
    auto arr3 = sparrow::build(l);
    /////////////////////
    // using any range
    auto iota = std::views::iota(1, 6)
                | std::views::transform(
                    [](int i)
                    {
                        return static_cast<int>(i);
                    }
                );
    auto arr4 = sparrow::build(iota);
    /////////////////////
    // all of the arrays above are equivalent to the manually built array
    auto arr5 = sparrow::primitive_array<int>({1, 2, 3, 4, 5});
    assert(arr == arr2);
    assert(arr == arr3);
    assert(arr == arr4);
    assert(arr == arr5);
    return EXIT_SUCCESS;
}

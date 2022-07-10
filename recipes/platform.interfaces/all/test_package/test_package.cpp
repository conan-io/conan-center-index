#include <iostream>
#include <ranges>
#include <vector>
#include <set>

#include <Platform.Interfaces.h>

using namespace Platform::Interfaces;

void print(IEnumerable auto&& enumerable)
{
    auto size = std::ranges::size(enumerable);

    std::cout << '[';
    for (int i = 0; auto&& item : enumerable)
    {
        std::cout << item;
        if (i < size - 1)
        {
            std::cout << ", ";
        }

        i++;
    }
    std::cout << ']' << std::endl;
}

template<IEnumerable Collection, typename Item = typename Enumerable<Collection>::Item>
requires
    IList<Collection> ||
    ISet<Collection> ||
    IDictionary<Collection>
void add(Collection& collection, const std::same_as<Item> auto& item)
{
    if constexpr (IList<Collection>)
    {
        collection.push_back(item);
    }
    else
    {
        collection.insert(item);
    }
}

int main()
{
    std::vector v { 1, 2, 3 };
    std::set s { 1, 2, 3 };

    add(v, 2); // 1 2 3 2
    add(v, 1); // 1 2 3 2 1

    add(s, 2); // 1 2 3
    add(s, 1); // 1 2 3
    add(s, 0); // 0 1 2 3


    print(v); // print: [1, 2, 3, 2, 1]
    print(s); // print: [0, 1, 2, 3]
}

#include <set>

#include <Platform.Delegates.h>
using namespace Platform::Delegates;

template<typename T>
struct EventfulSet : public std::set<T>
{
    using base = std::set<T>;

    template<typename... Args>
    EventfulSet(Args&&... args) : base(args...) {}

    MulticastDelegate<void(T&&)> InsertEvent{};
    MulticastDelegate<void(T&&)> InsertDuplicateEvent{};

    void insert(T&& item)
    {
        InsertEvent(std::forward<decltype(item)>(item));

        if (this->find(std::forward<decltype(item)>(item)) != this->end()) {
            InsertDuplicateEvent(std::forward<decltype(item)>(item));
        }

        base::insert(std::forward<decltype(item)>(item));
    }
};

int main()
{
    std::list<int> duplicates;

    EventfulSet<int> set;
    set.InsertEvent += std::function{[](int&& item) { std::cout << "insert to list: " << item << std::endl; }};
    set.InsertDuplicateEvent += std::function{[&](int&& item) { duplicates.push_back(item); }};

    set.insert(1);
    set.insert(2);
    set.insert(3);
    set.insert(1);
    set.insert(0);
    set.insert(2);
    set.insert(3);

    std::cout << "set is: ";
    for (auto item : set) {
        std::cout << item << " ";
    }
    std::cout << std::endl;

    std::cout << "captured duplicates: ";
    for (auto item : duplicates) {
        std::cout << item << " ";
    }
    std::cout << std::endl;
    return 0;
}

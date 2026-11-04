#include <indirect.h>
#include <polymorphic.h>

#include <cstdlib>

class Base
{
public:
    virtual ~Base() {};
    virtual int getValue() const = 0;
};

class Derived : public Base
{
    int value;
public:
    Derived(int value_) : value(value_) {}
    int getValue() const { return value; } 
};

int main()
{
    xyz::indirect initial(EXIT_SUCCESS);
    xyz::polymorphic<Base> result(std::in_place_type<Derived>, *initial);
    return result->getValue();
}

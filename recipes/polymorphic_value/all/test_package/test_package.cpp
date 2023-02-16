#include <polymorphic_value.h>

using namespace isocpp_p0201;

struct BaseType {
  virtual int getValue() const = 0;
  virtual ~BaseType() = default;
};

struct DerivedType : BaseType {
  int value = EXIT_SUCCESS;
  int getValue() const override { return value; }
};

int main()
{
    polymorphic_value<BaseType> result{new DerivedType()};
    return result->getValue();
}

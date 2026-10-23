#ifndef GREETER_ACTIVATOR_IMPL_HPP
#define GREETER_ACTIVATOR_IMPL_HPP

#include "IGreeter.h"

class GreeterActivatorImpl final : public IGreeter
{
  public:
    GreeterActivatorImpl() = default;
    ~GreeterActivatorImpl() override = default;
    std::string Greet() override;
};

#endif // GREETER_ACTIVATOR_IMPL_HPP

#ifndef GREETER_DS_IMPL_HPP
#define GREETER_DS_IMPL_HPP

#include "IGreeter.h"

class GreeterDSImpl final : public IGreeter
{
  public:
    GreeterDSImpl() = default;
    ~GreeterDSImpl() override = default;
    std::string Greet() override;
};

#endif // GREETER_DS_IMPL_HPP

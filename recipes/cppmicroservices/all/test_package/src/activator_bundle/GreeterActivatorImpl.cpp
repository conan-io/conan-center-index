#include "GreeterActivatorImpl.hpp"

#include <cppmicroservices/BundleActivator.h>
#include <cppmicroservices/BundleContext.h>

#include <memory>

std::string
GreeterActivatorImpl::Greet()
{
    return "Hello from Activator!";
}

class GreeterActivator : public cppmicroservices::BundleActivator
{
    void
    Start(cppmicroservices::BundleContext ctx) override
    {
        ctx.RegisterService<IGreeter>(std::make_shared<GreeterActivatorImpl>());
    }

    void
    Stop(cppmicroservices::BundleContext) override
    {
    }
};

CPPMICROSERVICES_EXPORT_BUNDLE_ACTIVATOR(GreeterActivator)

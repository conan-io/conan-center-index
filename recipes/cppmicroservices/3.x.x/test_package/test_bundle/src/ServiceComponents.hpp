#ifndef TEST_BUNDLE_SERVICE_COMPONENTS_HPP
#define TEST_BUNDLE_SERVICE_COMPONENTS_HPP

#include <string>

#include <cppmicroservices/GlobalConfig.h>

class US_ABI_EXPORT TestBundle
{
public:
    virtual ~TestBundle() = default;
    virtual std::string Description() const = 0;
};

class TestBundleImpl final : public TestBundle
{
public:
    TestBundleImpl() = default;
    ~TestBundleImpl() = default;
    
    std::string Description() const override;
};

#endif

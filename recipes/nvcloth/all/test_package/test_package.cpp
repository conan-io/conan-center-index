#include <iostream>
#include <PxPhysicsAPI.h>
#include <NvCloth/Factory.h>
class ProfilerCallback final : public physx::PxProfilerCallback
{
public:
    ProfilerCallback()
    {
    }

    ~ProfilerCallback()
    {
    }

    virtual void* zoneStart(const char* eventName, bool detached, uint64_t contextId)
    {
        return nullptr;
    }

    virtual void zoneEnd(void* profilerData, const char* eventName, bool detached, uint64_t contextId)
    {
    }
};

int main()
{
    auto defaultAllocatorCallback = physx::PxDefaultAllocator();
    auto defaultErrorCallback = physx::PxDefaultErrorCallback();
    auto defaultProfilerCallback = ProfilerCallback();
    nv::cloth::InitializeNvCloth(&defaultAllocatorCallback, &defaultErrorCallback, nv::cloth::GetNvClothAssertHandler(), &defaultProfilerCallback);
    std::cout << "Hello, NvCloth!" << std::endl;
    nv::cloth::Factory* factory = NvClothCreateFactoryCPU();
    if (factory == nullptr)
    {
        std::cout << "Failed to create factory" << std::endl;
        return -1;
    }

    NvClothDestroyFactory(factory);
    return 0;
}

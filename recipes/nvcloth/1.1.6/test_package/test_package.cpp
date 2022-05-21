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
        return 0;
    }

    virtual void zoneEnd(void* profilerData, const char* eventName, bool detached, uint64_t contextId)
    {
    }
};

int main()
{
    physx::PxDefaultAllocator defaultAllocatorCallback = physx::PxDefaultAllocator();
    physx::PxDefaultErrorCallback defaultErrorCallback = physx::PxDefaultErrorCallback();
    ProfilerCallback defaultProfilerCallback = ProfilerCallback();
    nv::cloth::InitializeNvCloth(&defaultAllocatorCallback, &defaultErrorCallback, nv::cloth::GetNvClothAssertHandler(), &defaultProfilerCallback);
    std::cout << "Hello, NvCloth!" << std::endl;
    nv::cloth::Factory* factory = NvClothCreateFactoryCPU();
    if (factory == 0)
    {
        std::cout << "Failed to create factory" << std::endl;
        return -1;
    }

    NvClothDestroyFactory(factory);
    return 0;
}

#include <iostream>
#include <NvCloth/Factory.h>
#include <foundation/PxAllocatorCallback.h>
#include <foundation/PxErrorCallback.h>
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

class AllocatorCallback : public physx::PxAllocatorCallback
{
public:
    AllocatorCallback()
    {
    }

    ~AllocatorCallback()
    {
    }

    virtual void* allocate(size_t size, const char* typeName, const char* filename, int line)
    {
        return malloc(size);
    }

    virtual void deallocate(void* ptr)
    {
        free(ptr);
    }
};

class ErrorCallback : public physx::PxErrorCallback
{
public:
    ErrorCallback()
    {
    }

    ~ErrorCallback()
    {
    }

    virtual void reportError(physx::PxErrorCode::Enum code, const char* message, const char* file, int line)
    {
        std::cout << "Error: " << message << " in " << file << ":" << line << std::endl;
    }
};

int main()
{
    AllocatorCallback defaultAllocatorCallback = AllocatorCallback();
    ErrorCallback defaultErrorCallback = ErrorCallback();
    ProfilerCallback defaultProfilerCallback = ProfilerCallback();
    nv::cloth::InitializeNvCloth(&defaultAllocatorCallback, &defaultErrorCallback, nv::cloth::GetNvClothAssertHandler(), &defaultProfilerCallback);
    nv::cloth::Factory* factory = NvClothCreateFactoryCPU();
    if (factory == 0)
    {
        std::cout << "Failed to create factory" << std::endl;
        return -1;
    }

    std::cout << "Hello, NvCloth!" << std::endl;
    NvClothDestroyFactory(factory);
    return 0;
}

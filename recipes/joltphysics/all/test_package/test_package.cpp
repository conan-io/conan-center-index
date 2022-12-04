#include <Jolt/Jolt.h>
#include <Jolt/RegisterTypes.h>
#include <Jolt/Core/Factory.h>
#include <Jolt/Core/TempAllocator.h>
#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSettings.h>

#include <cstdarg>
#include <iostream>
#include <thread>

static void TraceImpl(const char *inFMT, ...)
{
    va_list list;
    va_start(list, inFMT);
    char buffer[1024];
    std::vsnprintf(buffer, sizeof(buffer), inFMT, list);
    va_end(list);

    std::cout << buffer << std::endl;
}

int main()
{
    JPH::RegisterDefaultAllocator();

    JPH::Trace = TraceImpl;
    JPH_IF_ENABLE_ASSERTS(AssertFailed = JPH::AssertFailedImpl;)

    JPH::Factory::sInstance = new JPH::Factory();

    JPH::RegisterTypes();

    JPH::TempAllocatorImpl temp_allocator(10 * 1024 * 1024);
    JPH::JobSystemThreadPool job_system(JPH::cMaxPhysicsJobs, JPH::cMaxPhysicsBarriers, std::thread::hardware_concurrency() - 1);

    delete JPH::Factory::sInstance;
    JPH::Factory::sInstance = nullptr;

    return 0;
}

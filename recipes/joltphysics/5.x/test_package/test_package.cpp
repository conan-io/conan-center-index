#include <cstdlib>
#include <Jolt/Jolt.h>
#include <Jolt/Core/Factory.h>
#include <Jolt/RegisterTypes.h>


int main() {
    JPH::RegisterDefaultAllocator();
    auto factory = JPH::Factory();
    JPH::UnregisterTypes();
    return EXIT_SUCCESS;
}

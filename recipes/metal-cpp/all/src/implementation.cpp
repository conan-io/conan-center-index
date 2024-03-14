#define NS_PRIVATE_IMPLEMENTATION
#define CA_PRIVATE_IMPLEMENTATION
#define MTL_PRIVATE_IMPLEMENTATION

#ifdef HAS_METALFX
#define MTLFX_PRIVATE_IMPLEMENTATION
#endif  // HAS_METALFX

#include <Foundation/Foundation.hpp>
#include <Metal/Metal.hpp>
#include <QuartzCore/QuartzCore.hpp>

#ifdef HAS_METALFX
#include <MetalFX/MetalFX.hpp>
#endif  // HAS_METALFX

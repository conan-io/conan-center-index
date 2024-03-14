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

//! @file
//!       Helper file to allow the build as a library, as an implementation is needed but the
//!       metal-cpp package is shipped as "header-only".

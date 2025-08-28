#include <bx/bx.h>
#include <bx/allocator.h>
#include <bx/platform.h>
#include <bx/math.h>
#include <bx/debug.h>
#include <bx/string.h>
#include <bimg/bimg.h>
#include <bimg/decode.h>
#include <stdio.h>

//Important: bgfx shared on windows only works with the C99 API, the C++ API is not exported
#if BGFX_SHARED_LIB_USE && (BX_PLATFORM_WINDOWS || BX_PLATFORM_WINRT)
#include <bgfx/c99/bgfx.h>
#else
#include <bgfx/bgfx.h>
#endif


int main() {
	//test bx
	float tLerp = bx::lerp(0.0f, 10.0f, 0.5f);
    BX_TRACE("Lerped 0.0f to 10.0f at 0.5f, result %f", tLerp);
    BX_ASSERT(bx::isEqual(tLerp, 5.0f, 0.1f), "isEqual failed");
	bx::debugPrintf("Length of \"test\" is: %d", bx::strLen("test"));

	//test bimg
	auto format = bimg::getFormat("PNG");
	printf("Texture format: %d", format);

	//test bgfx
#if BGFX_SHARED_LIB_USE && (BX_PLATFORM_WINDOWS || BX_PLATFORM_WINRT)
	bgfx_init_t init;
	bgfx_init_ctor(&init);
	init.type     = bgfx_renderer_type::BGFX_RENDERER_TYPE_NOOP;
	init.vendorId = BGFX_PCI_ID_NONE;
	init.platformData.nwh  = nullptr;
	init.platformData.ndt  = nullptr;
	init.resolution.width  = 0;
	init.resolution.height = 0;
	init.resolution.reset  = BGFX_RESET_NONE;
	bgfx_init(&init);
	bgfx_shutdown();
    return 0;
#else
	bgfx::Init init;
	init.type     = bgfx::RendererType::Noop;
	init.vendorId = BGFX_PCI_ID_NONE;
	init.platformData.nwh  = nullptr;
	init.platformData.ndt  = nullptr;
	init.resolution.width  = 0;
	init.resolution.height = 0;
	init.resolution.reset  = BGFX_RESET_NONE;
	bgfx::init(init);
    bgfx::shutdown();
#endif
}

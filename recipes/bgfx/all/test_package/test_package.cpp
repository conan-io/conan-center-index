//Important: bgfx shared on windows only works with the C99 API, the C++ API is not exported
#include <bx/platform.h>

#if BGFX_SHARED_LIB_USE && (BX_PLATFORM_WINDOWS || BX_PLATFORM_WINRT)
#include <bgfx/c99/bgfx.h>
#else
#include <bgfx/bgfx.h>
#endif

int main() {
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

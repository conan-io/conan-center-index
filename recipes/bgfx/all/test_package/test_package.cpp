#include <bgfx/bgfx.h>

int main() {
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
    return 0;
}

#include "Common/interface/RefCntAutoPtr.hpp"
#include "Graphics/GraphicsEngine/interface/PipelineState.h"
#include "Graphics/GraphicsEngine/interface/SwapChain.h"
#include "Graphics/GraphicsEngine/interface/DeviceContext.h"
#include "Graphics/GraphicsEngine/interface/RenderDevice.h"

int main()
{
  Diligent::RefCntAutoPtr<Diligent::IRenderDevice>  _pDevice;
  Diligent::RefCntAutoPtr<Diligent::IDeviceContext> _pImmediateContext;
  Diligent::RefCntAutoPtr<Diligent::ISwapChain>     _pSwapChain;
  return 0;
}

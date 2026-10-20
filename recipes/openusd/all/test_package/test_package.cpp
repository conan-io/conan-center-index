#include <cstdlib>
#include <iostream>

#include <pxr/base/plug/plugin.h>
#include <pxr/base/plug/registry.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usdGeom/xform.h>

PXR_NAMESPACE_USING_DIRECTIVE

int main() {
  UsdStageRefPtr stage = UsdStage::CreateInMemory();
  UsdGeomXform::Define(stage, SdfPath("/root"));

#ifdef OPENUSD_WITH_IMAGING
  // hioOpenEXR is never linked by this executable: it's a runtime plugin
  // discovered through USD's Plug registry (plugInfo.json). Finding and
  // loading it here proves that discovery works from an installed package.
  PlugPluginPtr plugin = PlugRegistry::GetInstance().GetPluginWithName("hioOpenEXR");
  if (!plugin || !plugin->Load()) {
    std::cerr << "hioOpenEXR plugin not discoverable/loadable" << std::endl;
    return EXIT_FAILURE;
  }
#endif

  return stage ? EXIT_SUCCESS : EXIT_FAILURE;
}

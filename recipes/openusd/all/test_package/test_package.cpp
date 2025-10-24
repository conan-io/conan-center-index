#include <pxr/base/tf/token.h>
#include <pxr/usd/sdf/path.h>
#include <pxr/usd/usd/stage.h>
#include <pxr/usd/usd/zipFile.h>
#include <pxr/usd/usdGeom/mesh.h>
#include <pxr/usd/usdGeom/metrics.h>
#include <pxr/usd/usdGeom/primvar.h>
#include <pxr/usd/usdGeom/primvarsAPI.h>
#include <pxr/usd/usdGeom/xform.h>
#include <pxr/usd/usdShade/material.h>
#include <pxr/usd/usdShade/materialBindingAPI.h>
#include <pxr/usd/usdShade/shader.h>
#include <pxr/usdImaging/usdImaging/tokens.h>

PXR_NAMESPACE_USING_DIRECTIVE

int main(int argc, char *argv[]) {
  UsdStageRefPtr stage = UsdStage::CreateNew("HelloWorld.usda");

  UsdGeomSetStageUpAxis(stage, UsdGeomTokens->y);
  UsdGeomSetStageMetersPerUnit(stage, 0.01);

  // create mesh
  UsdGeomXform xform = UsdGeomXform::Define(stage, SdfPath("/root"));
  UsdGeomMesh mesh = UsdGeomMesh::Define(stage, SdfPath("/root/mesh"));
  stage->SetDefaultPrim(xform.GetPrim());

  // stage->GetRootLayer()->Save();

  return EXIT_SUCCESS;
}

#include <ogrsf_frmts.h>

#include <cstdio>
#include <cstdlib>

int main() {
  GDALAllRegister();

  const char *pszDriverName = "ESRI Shapefile";
  GDALDriver *poDriver = GetGDALDriverManager()->GetDriverByName(pszDriverName);
  if (!poDriver) {
    printf("%s driver not available.\n", pszDriverName);
    exit(1);
  }

  GDALDataset *poDS = poDriver->Create("point_out_cpp.shp", 0, 0, 0, GDT_Unknown, NULL);
  if (!poDS) {
    printf("Creation of output file failed.\n");
    exit(1);
  }

  OGRLayer *poLayer = poDS->CreateLayer("point_out", NULL, wkbPoint, NULL);
  if (!poLayer) {
    printf("Layer creation failed.\n");
    exit(1);
  }

  OGRFieldDefn oField("Name", OFTString);
  oField.SetWidth(32);

  if (poLayer->CreateField(&oField) != OGRERR_NONE) {
    printf("Creating Name field failed.\n");
    exit(1);
  }

  OGRFeature *poFeature = OGRFeature::CreateFeature(poLayer->GetLayerDefn());
  poFeature->SetField("Name", "conan");

  OGRPoint pt;
  pt.setX(40.74);
  pt.setY(-27.891);
  poFeature->SetGeometry(&pt);

  if (poLayer->CreateFeature(poFeature) != OGRERR_NONE) {
    printf("Failed to create feature in shapefile.\n");
    exit( 1 );
  }

  OGRFeature::DestroyFeature(poFeature);

  GDALClose(poDS);

  return 0;
}

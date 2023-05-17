#include <gdal.h>

#include <stdio.h>
#include <stdlib.h>

int main() {
  GDALAllRegister();

  const char *pszDriverName = "ESRI Shapefile";
  GDALDriverH hDriver = GDALGetDriverByName(pszDriverName);
  if (!hDriver) {
    printf("%s driver not available.\n", pszDriverName);
    exit(1);
  }

  GDALDatasetH hDS = GDALCreate(hDriver, "point_out_c.shp", 0, 0, 0, GDT_Unknown, NULL);
  if (!hDS) {
    printf("Creation of output file failed.\n");
    exit(1);
  }

  OGRLayerH hLayer = GDALDatasetCreateLayer(hDS, "point_out", NULL, wkbPoint, NULL);
  if (!hLayer) {
    printf("Layer creation failed.\n");
    exit(1);
  }

  OGRFieldDefnH hFieldDefn = OGR_Fld_Create("Name", OFTString);

  OGR_Fld_SetWidth(hFieldDefn, 32);

  if (OGR_L_CreateField(hLayer, hFieldDefn, TRUE) != OGRERR_NONE) {
    printf("Creating Name field failed.\n");
    exit(1);
  }

  OGR_Fld_Destroy(hFieldDefn);

  OGRFeatureH hFeature = OGR_F_Create(OGR_L_GetLayerDefn(hLayer));
  OGR_F_SetFieldString(hFeature, OGR_F_GetFieldIndex(hFeature, "Name"), "conan");

  OGRGeometryH hPt = OGR_G_CreateGeometry(wkbPoint);
  OGR_G_SetPoint_2D(hPt, 0, 40.74, -27.891);

  OGR_F_SetGeometry(hFeature, hPt);
  OGR_G_DestroyGeometry(hPt);

  if (OGR_L_CreateFeature(hLayer, hFeature) != OGRERR_NONE) {
    printf("Failed to create feature in shapefile.\n");
    exit(1);
  }

  OGR_F_Destroy(hFeature);

  GDALClose(hDS);

  return 0;
}

#include <spatialindex/capi/sidx_api.h>

#include <string.h>

int main() {
  double min[] = {0.5, 0.5};
  double max[] = {0.5, 0.5};
  int nDims = 2;
  int nId = 1;

  char pszData[5];

  IndexPropertyH props = IndexProperty_Create();
  IndexProperty_SetIndexType(props, RT_RTree);
  IndexProperty_SetIndexStorage(props, RT_Memory);
  IndexH idx = Index_Create(props);
  IndexProperty_Destroy(props);
  Index_InsertData(idx, nId, min, max, nDims, (uint8_t *)pszData, strlen(pszData) + 1);
  Index_Destroy(idx);

  return 0;
}

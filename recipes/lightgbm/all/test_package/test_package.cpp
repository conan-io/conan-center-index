#include <LightGBM/c_api.h>

int main() {
    float mat[] = {1, 2, 3, 4, 5, 6};
    DatasetHandle datasetHandle = nullptr;
    LGBM_DatasetCreateFromMat(mat, C_API_DTYPE_FLOAT32, 1, 6, 0, "", nullptr, &datasetHandle);
    BoosterHandle boosterHandle = nullptr;
    LGBM_BoosterCreate(datasetHandle, "", &boosterHandle);
    LGBM_BoosterFree(boosterHandle);
    LGBM_DatasetFree(datasetHandle);
    return 0;
}

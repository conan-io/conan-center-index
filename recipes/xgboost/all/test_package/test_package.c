#include <xgboost/c_api.h>

int main() {
    int silent = 0;
    DMatrixHandle dtrain;
    XGDMatrixCreateFromFile("missing.txt", silent, &dtrain);
}

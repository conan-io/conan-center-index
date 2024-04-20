#include <xgboost/c_api.h>

int main() {
    BoosterHandle booster;
    XGBoosterSetParam(booster, "objective", "binary:logistic");
}

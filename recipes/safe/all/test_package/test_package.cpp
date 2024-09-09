#include "safe/safe.h"

int main(void) {
    safe::Safe<int> safeValue;

    {
        safe::WriteAccess<safe::Safe<int>> value(safeValue);
        *value = 5;
    }
    
    return 0;
}

#include "simfil/value.h"

int main() {
    auto value = simfil::Value::make((int64_t)123);
    (void)value;

    return 0;
}

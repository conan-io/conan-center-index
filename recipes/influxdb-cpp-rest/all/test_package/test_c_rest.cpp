#include <influx_c_rest_lines.h>

int main()
{
    auto* values = influx_c_rest_key_value_pairs_new();
    influx_c_rest_key_value_pairs_destroy(values);
    return 0;
}

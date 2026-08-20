#include <influx_c_rest_lines.h>
#include <cstring>

int main()
{
    influx_c_rest_key_value_pairs_t* values = influx_c_rest_key_value_pairs_new();
    influx_c_rest_key_value_pairs_add_int(values, "value", 42);

    influx_c_rest_lines_t* lines = influx_c_rest_lines_new_measurement("measurement", nullptr, values);
    const char* result = influx_c_rest_lines_get(lines);

    const bool ok = result != nullptr
        && std::strstr(result, "measurement") != nullptr
        && std::strstr(result, "value=42i") != nullptr;

    influx_c_rest_lines_destroy(lines);
    influx_c_rest_key_value_pairs_destroy(values);

    return ok ? 0 : 1;
}

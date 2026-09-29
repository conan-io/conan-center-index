#include <ftms/control.h>
int main(void) {
    ftms_control_request request = {FTMS_CONTROL_SET_TARGET_RESISTANCE};
    ftms_control_format_options format = {FTMS_CONTROL_RESISTANCE_UINT8_TENTHS};
    unsigned char bytes[2]; size_t written = 0;
    request.value.resistance_tenth_level = 42;
    return ftms_encode_control_request_with_format(&request, &format, bytes, sizeof(bytes), &written) != FTMS_OK || written != 2 || bytes[0] != 4 || bytes[1] != 42;
}

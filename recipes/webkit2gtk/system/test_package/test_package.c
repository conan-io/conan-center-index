#include <webkit2/webkit2.h>

int main(void) {
    return webkit_get_major_version() > 0 ? 0 : 1;
}

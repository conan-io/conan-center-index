#include <pipewire/pipewire.h>

int main(void) {
    return pw_check_library_version(0, 3, 75) == 0;
}

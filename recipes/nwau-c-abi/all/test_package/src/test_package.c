#include <nwau_abi.h>

int main(void) {
    if (nwau_abi_version_major() != 0) {
        return 1;
    }
    if (nwau_abi_version_minor() != 1) {
        return 2;
    }
    if (nwau_abi_status_message(NWAU_ABI_STATUS_OK).ptr == NULL) {
        return 3;
    }
    return 0;
}

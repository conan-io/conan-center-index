#include <xnnpack.h>

int main() {
    int init_status = xnn_initialize(NULL);
    if(init_status != xnn_status_success) {
        return 1;
    }
    int deinit_status = xnn_deinitialize();
    if(deinit_status != xnn_status_success) {
        return 1;
    }
    return 0;
}

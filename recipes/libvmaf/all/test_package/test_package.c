#include <libvmaf/libvmaf.h>

#include <stdio.h>

int main(void) {
    VmafConfiguration cfg = {
        .log_level = VMAF_LOG_LEVEL_NONE,
        .n_threads = 1,
    };

    VmafContext *vmaf = NULL;
    if (vmaf_init(&vmaf, cfg) != 0) {
        fprintf(stderr, "vmaf_init failed\n");
        return 1;
    }

    vmaf_close(vmaf);
    printf("libvmaf initialized successfully\n");
    return 0;
}

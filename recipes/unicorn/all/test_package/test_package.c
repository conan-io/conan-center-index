#include "unicorn/unicorn.h"

#include <stdio.h>

// x86 code to be emulated
#define X86_CODE32 "\x90\x41\x4a" // NOP; INC ecx; DEC edx;

// memory address where emulation starts
#define ADDRESS 0x1000000

static int emul_x86() {
    uc_engine *uc;
    uc_err err;

    printf("Emulate i386 code\n");

    int r_ecx = 0x1234;     // ECX register
    int r_edx = 0x7890;     // EDX register

    printf("CPU context before:\n", r_ecx);
    printf(">>> ECX = 0x%x\n", r_ecx);
    printf(">>> EDX = 0x%x\n", r_edx);

    // Initialize emulator in X86-32bit mode
    err = uc_open(UC_ARCH_X86, UC_MODE_32, &uc);
    if (err != UC_ERR_OK) {
        printf("Failed on uc_open() with error returned: %u\n", err);
        return -1;
    }

    // map 2MB memory for this emulation
    uc_mem_map(uc, ADDRESS, 2 * 1024 * 1024, UC_PROT_ALL);

    // write machine code to be emulated to memory
    if (uc_mem_write(uc, ADDRESS, X86_CODE32, sizeof(X86_CODE32) - 1)) {
        printf("Failed to write emulation code to memory, quit!\n");
        return -1;
    }

    // initialize machine registers
    uc_reg_write(uc, UC_X86_REG_ECX, &r_ecx);
    uc_reg_write(uc, UC_X86_REG_EDX, &r_edx);

    // emulate code in infinite time & unlimited instructions
    err = uc_emu_start(uc, ADDRESS, ADDRESS + sizeof(X86_CODE32) - 1, 0, 0);
    if (err) {
        printf("Failed on uc_emu_start() with error returned %u: %s\n",
            err, uc_strerror(err));
    }

    // now print out some registers
    printf("Emulation done. CPU context\n");

    uc_reg_read(uc, UC_X86_REG_ECX, &r_ecx);
    uc_reg_read(uc, UC_X86_REG_EDX, &r_edx);
    printf(">>> ECX = 0x%x\n", r_ecx);
    printf(">>> EDX = 0x%x\n", r_edx);

    uc_close(uc);
    return 0;
}


int main() {
    unsigned int major, minor;
    uc_version(&major, &minor);
    printf("unicorn version %d.%d\n", major, minor);

    if (uc_arch_supported(UC_ARCH_X86)) {
        return emul_x86();
    }
    return 0;
}

#include <stdio.h>
#include <stdlib.h>

#include <fcntl.h>
#ifdef _MSC_VER
#include <io.h>
#else
#include <unistd.h>
#endif

#include "libelf.h"

int main(int argc , char **argv) {
    int fd;
    Elf *e;
    const char *k;
    Elf_Kind  ek;

    if (elf_version(EV_CURRENT) ==  EV_NONE) {
        printf("ELF library initialization failed: %s\n", elf_errmsg ( -1));
        return EXIT_FAILURE;
    }

#ifdef _WIN32
    return EXIT_SUCCESS;
#endif

#ifdef _MSVC_VER
    if ((fd = _open(argv[0], _O_RDONLY , 0)) < 0) {
#else
    if ((fd = open(argv[0], O_RDONLY , 0)) < 0) {
#endif
        printf("open %s failed\n", argv [0]);
        return EXIT_FAILURE;
    }

    if(ELF_C_NULL != 0)
    {
        printf("ELF_C_NULL has wrong value: %d\n", ELF_C_NULL);
        return EXIT_FAILURE;
    }
    if(ELF_C_READ != 1)
    {
        printf("ELF_C_READ has wrong value: %d\n", ELF_C_READ);
        return EXIT_FAILURE;
    }
    if(ELF_C_WRITE != 2)
    {
        printf("ELF_C_WRITE has wrong value: %d\n", ELF_C_WRITE);
        return EXIT_FAILURE;
    }
    if(ELF_C_CLR != 3)
    {
        printf("ELF_C_CLR has wrong value: %d\n", ELF_C_CLR);
        return EXIT_FAILURE;
    }
    if(ELF_C_SET != 4)
    {
        printf("ELF_C_SET has wrong value: %d\n", ELF_C_SET);
        return EXIT_FAILURE;
    }
    if(ELF_C_FDDONE != 5)
    {
        printf("ELF_C_FDDONE has wrong value: %d\n", ELF_C_FDDONE);
        return EXIT_FAILURE;
    }
    if(ELF_C_FDREAD != 6)
    {
        printf("ELF_C_FDREAD has wrong value: %d\n", ELF_C_FDREAD);
        return EXIT_FAILURE;
    }
    if(ELF_C_RDWR != 7)
    {
        printf("ELF_C_RDWR has wrong value: %d\n", ELF_C_RDWR);
        return EXIT_FAILURE;
    }
    if(ELF_C_NUM != 8)
    {
        printf("ELF_C_NUM has wrong value: %d\n", ELF_C_NUM);
        return EXIT_FAILURE;
    }

    if ((e = elf_begin(fd, ELF_C_READ, NULL)) == NULL) {
        printf("elf_begin () failed: %s.\n", elf_errmsg ( -1));
        return EXIT_FAILURE;
    }

    ek = elf_kind(e);

    switch (ek) {
        case  ELF_K_AR:
            k = "ar(1) archive";
            break;
        case  ELF_K_ELF:
            k = "elf object";
            break;
        case  ELF_K_NONE:
            k = "data";
            break;
        default:
            k = "unrecognized";
    }

    printf("%s: %s\n", argv[0], k);
    elf_end(e);

#ifdef _MSVC_VER
    _close(fd);
#else
    close(fd);
#endif

    return EXIT_SUCCESS;
}

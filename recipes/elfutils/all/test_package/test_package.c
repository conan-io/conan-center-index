#include <gelf.h>
#include <elfutils/libasm.h>
#include <elfutils/libdwelf.h>
#include <elfutils/libdwfl.h>
#include <elfutils/libdw.h>
//#include <elfutils/libebl.h>
#include <dwarf.h>
#include <libelf.h>

#include <stdio.h>
#include <stdlib.h>

#include <fcntl.h>
#ifdef _MSC_VER
#include <io.h>
#else
#include <unistd.h>
#endif

int main(int argc , char **argv)
{
    int fd;
    Elf *e;
    const char *k;
    Elf_Kind  ek;


    if (argc < 2)
    {
        printf("Usage: %s <binary>", argv[0]);
        return -1;
    }


    if (elf_version(EV_CURRENT) ==  EV_NONE) {
        printf("ELF library initialization failed: %s\n", elf_errmsg ( -1));
        return EXIT_FAILURE;
    }

#ifdef _WIN32
    return EXIT_SUCCESS;
#endif

#ifdef _MSVC_VER
    if ((fd = _open(argv[1], _O_RDONLY , 0)) < 0) {
#else
    if ((fd = open(argv[1], O_RDONLY , 0)) < 0) {
#endif
        printf("open %s failed\n", argv [0]);
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

    printf("%s: %s\n", argv[1], k);
    elf_end(e);

#ifdef _MSVC_VER
    _close(fd);
#else
    close(fd);
#endif

    return EXIT_SUCCESS;
}

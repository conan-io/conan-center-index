#include <stdio.h>

#include <frozen/map.h>

#define ELF_RELOC(name, value) name = value,

/** i386 relocations. */
enum class RELOC_i386 {
	/* TODO: this is just a subset */
	ELF_RELOC(R_386_NONE,           0)
	ELF_RELOC(R_386_32,             1)
	ELF_RELOC(R_386_PC32,           2)
	ELF_RELOC(R_386_GOT32,          3)
	ELF_RELOC(R_386_PLT32,          4)
	ELF_RELOC(R_386_COPY,           5)
	ELF_RELOC(R_386_GLOB_DAT,       6)
	ELF_RELOC(R_386_JUMP_SLOT,      7)
	ELF_RELOC(R_386_RELATIVE,       8)
	ELF_RELOC(R_386_GOTOFF,         9)
};

constexpr frozen::map<RELOC_i386, const char*, 10> e2s = {
    { RELOC_i386::R_386_NONE,          "NONE"},
    { RELOC_i386::R_386_32,            "R32"},
    { RELOC_i386::R_386_PC32,          "PC32"},
    { RELOC_i386::R_386_GOT32,         "GOT32"},
    { RELOC_i386::R_386_PLT32,         "PLT32"},
    { RELOC_i386::R_386_COPY,          "COPY"},
    { RELOC_i386::R_386_GLOB_DAT,      "GLOB_DAT"},
    { RELOC_i386::R_386_JUMP_SLOT,     "JUMP_SLOT"},
    { RELOC_i386::R_386_RELATIVE,      "RELATIVE"},
    { RELOC_i386::R_386_GOTOFF,        "GOTOFF"}
};


int main()
{
	printf("%s\n", e2s.at(RELOC_i386::R_386_GOT32));
	return 0;
}

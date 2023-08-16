#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>

#ifndef LIBDWARF_NEW_STRUCTURE
    #include "dwarf.h"
    #include "libdwarf.h"
#else
    #include "libdwarf/libdwarf.h"
#endif

void example1(Dwarf_Die somedie) {
    Dwarf_Debug dbg = 0;
    Dwarf_Signed atcount;
    Dwarf_Attribute *atlist;
    Dwarf_Error error = 0;
    Dwarf_Signed i = 0;
    int errv;
    errv = dwarf_attrlist(somedie, &atlist, &atcount, &error);
    if (errv == DW_DLV_OK) {
        for (i = 0; i < atcount; ++i) {
            dwarf_dealloc(dbg, atlist[i], DW_DLA_ATTR);
        }
        dwarf_dealloc(dbg, atlist, DW_DLA_LIST);
    }
    else if(errv == DW_DLV_ERROR){
        dwarf_dealloc(dbg, error, DW_DLA_ERROR);
    }
}
int main(void){
    Dwarf_Die somedie;
    memset(&somedie, 0, sizeof(somedie));
    example1(somedie);
    return EXIT_SUCCESS;
}

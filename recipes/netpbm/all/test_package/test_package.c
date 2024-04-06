// source: https://netpbm.sourceforge.net/doc/libnetpbm_ug.html

#include <netpbm/pam.h>

void pam_example() {
    struct pam inpam, outpam;
    tuple * tuplerow;
    unsigned int row;

    pm_init("image.pam", 0);

    pnm_readpaminit(stdin, &inpam, PAM_STRUCT_SIZE(tuple_type));

    outpam = inpam;
    outpam.file = stdout;

    pnm_writepaminit(&outpam);

    tuplerow = pnm_allocpamrow(&inpam);

    int grand_total = 0;
    for (row = 0; row < inpam.height; ++row) {
       unsigned int column;
       pnm_readpamrow(&inpam, tuplerow);
       for (column = 0; column < inpam.width; ++column) {
           unsigned int plane;
           for (plane = 0; plane < inpam.depth; ++plane) {
               grand_total += tuplerow[column][plane];
           }
       }
       pnm_writepamrow(&outpam, tuplerow);
    }
    pnm_freepamrow(tuplerow);
}

int main() {
    return 0;
}

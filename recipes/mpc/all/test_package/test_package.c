/* example was taken from https://www.gnu.org/ghm/2011/paris/slides/andreas-enge-mpc.pdf */

#include <stdio.h>
#include <mpc.h>

int main (void) {
    mpc_t z;
    int inex;
    mpc_init2 (z, 123);
    mpc_set_ui_ui (z, 0, 2, MPC_RNDNN);
    inex = mpc_asin (z, z, MPC_RNDNN);
    mpc_out_str (stdout, 10, 0, z, MPC_RNDNN);
    printf ("\n%i %i\n", MPC_INEX_RE (inex), MPC_INEX_IM (inex));
    mpc_clear (z);
    return 0;
}

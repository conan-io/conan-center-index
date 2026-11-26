#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <rpc/rpc.h>
#include <rpc/rpc_com.h>


int main(void) {
    char buf[RPC_MAXDATASIZE];

    XDR xdr_in;
    xdrmem_create(&xdr_in, buf, sizeof(buf), XDR_ENCODE);
    printf("XDR_ENCODE: %d\n", xdr_in.x_op);

    return EXIT_SUCCESS;
}

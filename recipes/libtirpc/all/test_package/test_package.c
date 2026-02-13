#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <rpc/rpc.h>
#include <rpc/rpc_com.h>


int main(void) {
    char buf[RPC_MAXDATASIZE];

    XDR xdr_in;
    xdrmem_create(&xdr_in, buf, sizeof(buf), XDR_ENCODE);

    char* data_in = "Hello World!";
    if (!xdr_string(&xdr_in, &data_in, strlen(data_in))) {
        return EXIT_FAILURE;
    }

    XDR xdr_out;
    xdrmem_create(&xdr_out, buf, sizeof(buf), XDR_DECODE);

    char* data_out = NULL;
    if (!xdr_string(&xdr_out, &data_out, sizeof(buf))) {
        return EXIT_FAILURE + 1;
    }

    if (strcmp(data_in, data_out) != 0) {
        return EXIT_FAILURE + 2;
    }
    return EXIT_SUCCESS;
}

#include <nng/nng.h>
#include <nng/protocol/reqrep0/rep.h>
#include <nng/protocol/reqrep0/req.h>
#include <nng/supplemental/util/platform.h>

int main(int argc, char **argv)
{
	int rc;
    nng_socket sock;
    rc = nng_req0_open(&sock);
    nng_close(sock);
    return 0;
}


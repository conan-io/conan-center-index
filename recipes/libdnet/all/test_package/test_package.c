#include <config.h>

#include <sys/types.h>

#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <dnet.h>

void addr_usage(void)
{
	fprintf(stderr, "Usage: dnet addr <address> ...\n");
	exit(1);
}

int main(int argc, char *argv[])
{
	struct addr addr;
	int c, len;

	if (argc == 1 || *(argv[1]) == '-')
		addr_usage();

	for (c = 1; c < argc; c++) {
		if (addr_aton(argv[c], &addr) < 0)
			addr_usage();

		len = addr.addr_bits / 8;

		if (write(STDOUT_FILENO, addr.addr_data8, len) != len)
			err(1, "write");
	}
	return 0;
}

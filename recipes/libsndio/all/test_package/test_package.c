#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sndio.h>

int main(int argc, char *argv[]) {
	int ch;
	unsigned mode = SIO_PLAY | SIO_REC;
	struct sio_hdl *hdl;

	hdl = sio_open(NULL, mode, 0);
	if (hdl == NULL) {
		fprintf(stderr, "sio_open() failed, but test is ok\n");
		exit(0);
	} else {
		printf("sio_open() success" );
	}
	sio_close(hdl);
	return 0;
}

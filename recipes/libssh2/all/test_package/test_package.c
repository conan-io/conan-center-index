#include <libssh2.h>

int main(int argc, char *argv[])
{
	LIBSSH2_SESSION* session = libssh2_session_init();
	libssh2_session_disconnect(session, "Normal Shutdown");
	libssh2_session_free(session);

	return 0;
}

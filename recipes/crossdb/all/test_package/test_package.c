#include <crossdb.h>

int main () {
	xdb_conn_t	*pConn = xdb_open (":memory:");
	XDB_CHECK (NULL != pConn, printf ("failed to create DB\n"); return -1;);

	xdb_close (pConn);

    return 0;
}

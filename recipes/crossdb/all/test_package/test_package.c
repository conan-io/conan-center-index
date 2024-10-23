#include <crossdb.h>

int main () {
	xdb_res_t	*pRes;
	xdb_row_t	*pRow;

	xdb_conn_t	*pConn = xdb_open (":memory:");
	XDB_CHECK (NULL != pConn, printf ("failed to create DB\n"); return -1;);

	// Create Table
	pRes = xdb_exec (pConn, "CREATE TABLE IF NOT EXISTS student (id INT PRIMARY KEY, name CHAR(16), age INT, class CHAR(16), score FLOAT, info CHAR(255))");
	XDB_RESCHK(pRes, printf ("Can't create table student\n"); goto error;);
	pRes = xdb_exec (pConn, "CREATE TABLE IF NOT EXISTS teacher (id INT PRIMARY KEY, name CHAR(16), age INT, info CHAR(255), INDEX (name))");
	XDB_RESCHK(pRes, printf ("Can't create table teacher\n"); goto error;);
	pRes = xdb_exec (pConn, "CREATE TABLE IF NOT EXISTS book (id INT PRIMARY KEY, name CHAR(64), author CHAR(32), count INT, INDEX (name))");
	XDB_RESCHK(pRes, printf ("Can't create table book\n"); goto error;);

	// clean table
	pRes = xdb_exec (pConn, "DELETE FROM student");
	pRes = xdb_exec (pConn, "DELETE FROM teacher");
	pRes = xdb_exec (pConn, "DELETE FROM book");

error:
	xdb_close (pConn);

    return 0;
}

#include <sqlite3.h>
#include <stddef.h>

int empty_xOpen(sqlite3_vfs *vfs, const char *zName, sqlite3_file *f, int flags, int *pOutFlags)
{
    // TODO: implement
    return SQLITE_OK;
}

int empty_xDelete(sqlite3_vfs *vfs, const char *zName, int syncDir)
{
    // TODO: implement
    return SQLITE_OK;
}

int empty_xAccess(sqlite3_vfs *vfs, const char *zName, int flags, int *pResOut)
{
    // TODO: implement
    return SQLITE_OK;
}

int empty_xFullPathname(sqlite3_vfs *vfs, const char *zName, int nOut, char *zOut)
{
    // TODO: implement
    return SQLITE_OK;
}
int empty_xRandomness(sqlite3_vfs *vfs, int nByte, char *zOut)
{
    // TODO: implement
    return SQLITE_OK;
}
int empty_xSleep(sqlite3_vfs *vfs, int microseconds)
{
    // TODO: implement
    return SQLITE_OK;
}
int empty_xCurrentTime(sqlite3_vfs *vfs, double *t)
{
    // TODO: implement
    return SQLITE_OK;
}
int empty_xGetLastError(sqlite3_vfs *vfs, int code, char *name)
{
    // TODO: implement
    return SQLITE_OK;
}
int empty_xCurrentTimeInt64(sqlite3_vfs *vfs, sqlite3_int64 *t)
{
    // TODO: implement
    return SQLITE_OK;
}

// empty VFS will be provided
int sqlite3_os_init(void)
{
    static sqlite3_vfs emptyVFS =
    {
        2, /* iVersion */
        0, /* szOsFile */
        100, /* mxPathname */
        NULL, /* pNext */
        "empty", /* zName */
        NULL, /* pAppData */
        empty_xOpen, /* xOpen */
        empty_xDelete, /* xDelete */
        empty_xAccess, /* xAccess */
        empty_xFullPathname, /* xFullPathname */
        NULL, /* xDlOpen */
        NULL, /* xDlError */
        NULL, /* xDlSym */
        NULL, /* xDlClose */
        empty_xRandomness, /* xRandomness */
        empty_xSleep, /* xSleep */
        empty_xCurrentTime, /* xCurrentTime */
        empty_xGetLastError, /* xGetLastError */
        empty_xCurrentTimeInt64, /* xCurrentTimeInt64 */
        NULL, /* xSetSystemCall */
        NULL, /* xGetSystemCall */
        NULL, /* xNextSystemCall */
    };

    sqlite3_vfs_register(&emptyVFS, 1);

    return SQLITE_OK;
}

int sqlite3_os_end(void)
{
    return SQLITE_OK;
}

#include <unqlite.h>

#include <stdio.h>

int main(void) {
    int i, rc;
    unqlite *pDb;

    rc = unqlite_open(&pDb, "test.db", UNQLITE_OPEN_CREATE);
    if (rc != UNQLITE_OK) return -1;

    rc = unqlite_kv_store(pDb, "test", -1, "Hello World", 11);
    if (rc != UNQLITE_OK) return -1;

    rc = unqlite_kv_store_fmt(pDb, "date", -1, "Current date: %d:%d:%d", 2013,06,07);
    if (rc != UNQLITE_OK) return -1;

    rc = unqlite_kv_append(pDb, "msg", -1, "Hello, ", 7);
    if (rc == UNQLITE_OK) {
        rc = unqlite_kv_append(pDb, "msg", -1, "Current time is: ", 17);
        if (rc == UNQLITE_OK) {
            rc = unqlite_kv_append_fmt(pDb, "msg", -1, "%d:%d:%d", 10, 16, 53);
        }
    }

    unqlite_kv_delete(pDb, "test", -1);

    for (i = 0 ; i < 20 ; ++i) {
        char zKey[12];
        char zData[34];

        unqlite_util_random_string(pDb, zKey, sizeof(zKey));

        rc = unqlite_kv_store(pDb, zKey, sizeof(zKey), zData, sizeof(zData));
        if (rc != UNQLITE_OK) break;
    }

    if (rc != UNQLITE_OK) {
        const char *zBuf;
        int iLen;
        unqlite_config(pDb, UNQLITE_CONFIG_ERR_LOG, &zBuf, &iLen);
        if (iLen > 0) {
            fprintf(stderr, "%s", zBuf);
        }
        if (rc != UNQLITE_BUSY && rc != UNQLITE_NOTIMPLEMENTED) {
            unqlite_rollback(pDb);
        }
    }

    unqlite_close(pDb);

    return 0;
}

// Test that Poco::DataPostgreSQL correctly propagates libpq dependency
// to consumers.
//
// SessionHandle.h directly includes <libpq-fe.h>. It is a public installed
// header of Poco::DataPostgreSQL, so any consumer must be able to include it.
#include <Poco/Data/PostgreSQL/SessionHandle.h>

int main() {
    // PGconn is the core libpq connection type declared in libpq-fe.h.
    // Simply forming a pointer to it is enough to verify that libpq-fe.h
    // was found via transitive include propagation through Poco::DataPostgreSQL.
    PGconn* conn = nullptr;
    (void)conn;
    return 0;
}

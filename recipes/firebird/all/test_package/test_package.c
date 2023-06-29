#include <stdlib.h>
#include <stdio.h>
#include <ibase.h>

int main (int argc, char** argv)
{
    isc_db_handle   newdb = 0;
    isc_tr_handle   trans = 0;
    ISC_STATUS_ARRAY status;
    long            sqlcode;

    char * creade_db_statement = "CREATE DATABASE 'new.fdb'";
    // This command will fail, but we ignore that for the purposes of this test
    isc_dsql_execute_immediate(status, &newdb, &trans, 0, creade_db_statement, 1, NULL);
    isc_commit_transaction(status, &trans);
    isc_detach_database(status, &newdb);

    return 0;
}

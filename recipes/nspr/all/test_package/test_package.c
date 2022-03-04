#include <nspr.h>

#include <stdio.h>

static int primordial(int argc, char *argv[]) {
    if (PR_Initialized() != PR_TRUE) {
        fprintf(stderr, "NSPR not initialized!\n");
        return 1;
    }
    fprintf(stderr, "Inside primordial function\n");
    return 0;
}

int main(int argc, char *argv[]) {
    int versionOk = PR_VersionCheck(PR_VERSION);
    if (versionOk == 0) {
        fprintf(stderr, "PR_VersionCheck() failed\n");
        return 1;
    }
    printf(PR_NAME " version %s\n", PR_GetVersion());
    PR_Initialize(primordial, argc, argv, 0);

    PR_ProcessExit(0);
    fprintf(stderr, "PR_ProcessExit failed\n");
    return 1;
}

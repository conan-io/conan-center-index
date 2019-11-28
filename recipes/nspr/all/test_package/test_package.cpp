#include <nspr.h>

#include <iostream>


static int primordial(int argc, char *argv[]) {
    if (PR_Initialized() != PR_TRUE) {
        std::cerr << "NSPR not initialized!\n";
        return 1;
    }
    std::cout << "Inside primordial function\n";
    return 0;
}


int main(int argc, char *argv[]) {
    bool versionOk = PR_VersionCheck(PR_VERSION);
    if (!versionOk) {
        std::cerr << "PR_VersionCheck() failed\n";
        return 1;
    }
    std::cout << PR_NAME << " version " << PR_GetVersion() << "\n";
    return PR_Initialize(primordial, argc, argv, 0);

    PR_Cleanup();

    PR_ProcessExit(0);
    std::cerr << "PR_ProcessExit faile\n";
    return 1;
}

#include "git2.h"

#include <cstdlib>
#include <iostream>

int main()
{
    git_libgit2_init();
    int versionMajor, versionMinor, versionRev;
    git_libgit2_version(&versionMajor, &versionMinor, &versionRev);

    std::cout << "libgit2 v" << versionMajor << "." << versionMinor << "." << versionRev << std::endl;

    std::cout << "Compile Features:" << std::endl;

    int features = git_libgit2_features();

    if (features & GIT_FEATURE_THREADS)
        std::cout << " - Thread safe" << std::endl;
    else
        std::cout << " - Single thread only" << std::endl;

    if (features & GIT_FEATURE_HTTPS)
        std::cout << " - TLS (openssl, mbedtls, winhttp or security)" << std::endl;
    else
        std::cout << " - No TLS" << std::endl;

    if (features & GIT_FEATURE_SSH)
        std::cout << " - SSH (libssh2)" << std::endl;
    else
        std::cout << " - No SSH support" << std::endl;

    git_libgit2_shutdown();
    return EXIT_SUCCESS;
}

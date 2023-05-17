#include <git2.h>

#include <stdio.h>

int main()
{
    git_libgit2_init();
    int versionMajor, versionMinor, versionRev;
    git_libgit2_version(&versionMajor, &versionMinor, &versionRev);

    printf("libgit2 v%i.%i.%i\n", versionMajor, versionMinor, versionRev);

    printf("Compile Features:\n");

    int features = git_libgit2_features();

    if (features & GIT_FEATURE_THREADS)
        printf(" - Thread safe\n");
    else
        printf(" - Single thread only\n");

    if (features & GIT_FEATURE_HTTPS)
        printf(" - TLS (openssl, mbedtls, winhttp or security)\n");
    else
        printf(" - No TLS\n");

    if (features & GIT_FEATURE_SSH)
        printf(" - SSH (libssh2)\n");
    else
        printf(" - No SSH support\n");

    git_libgit2_shutdown();
    return 0;
}

#include <physfs.h>

#include <stdio.h>

int main() {
    struct PHYSFS_Version physfs_version;
    PHYSFS_getLinkedVersion(&physfs_version);
    printf("PhysicsFS version %i.%i.%i", physfs_version.major, physfs_version.minor, physfs_version.patch);
    return 0;
}

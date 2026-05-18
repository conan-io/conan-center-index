#include <mujoco/mujoco.h>

#include <cstdio>

int main() {

    const char* version = mj_versionString();
    printf("MuJoCo Version: %s\n", version);

    return 0;
}

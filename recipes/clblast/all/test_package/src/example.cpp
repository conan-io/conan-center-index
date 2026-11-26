#include <cstdio>
#include <clblast.h>

int main() {
    auto status = clblast::ClearCache();
    printf("CLBlast ClearCache status: %d\n", static_cast<int>(status));
    return 0;
}

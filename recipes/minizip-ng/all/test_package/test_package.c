#include <stdlib.h>
#include <mz.h>
#include <mz_os.h>

int main(int argc, char** argv)
{
    char output[256];
    memset(output, 'z', sizeof(output));
    int32_t err = mz_path_resolve("c:\\test\\.", output, sizeof(output));
    int32_t ok = (strcmp(output, "c:\\test\\") == 0);
    return EXIT_SUCCESS;
}

#include <audio/audiolib.h>

#include <stdio.h>
#include <stdlib.h>

int main()
{
    AuServer *aud = NULL;
    printf("NAS test_package\n");
    aud = AuOpenServer(NULL, 0, NULL, 0, NULL, NULL);
    if (aud == NULL) {
        return EXIT_SUCCESS; /* Ignore failure */
    }
    AuCloseServer(aud);
    return EXIT_SUCCESS;
}

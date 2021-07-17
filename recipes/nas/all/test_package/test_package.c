
#include <stdio.h>

#include <audio/audiolib.h>

int main(void)
{
    printf("NAS test_package\n");


    AuServer* aud = AuOpenServer(NULL, 0, NULL, 0, NULL, NULL);
	return 0;
}

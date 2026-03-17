#include <fontconfig/fontconfig.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
	printf("Fontconfig version: %d\n", FcGetVersion());
    return EXIT_SUCCESS;
}

#include "jwt.h"
#include <stdio.h>

int main() {
    jwt_t *jwt = NULL;
	int ret = 0;
	ret = jwt_new(&jwt);
	jwt_free(jwt);
	printf("libjwt test package success\n");
    return 0;
}

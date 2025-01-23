#include "jwt.h"

int main() {
    
    jwt_t *jwt = NULL;
	int ret = 0;

	ret = jwt_new(&jwt);

	jwt_free(jwt);
    
    return ret; 
}

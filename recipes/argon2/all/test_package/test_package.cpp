#include "argon2.h"
#include <stdio.h>

int main() {
    const char *salt = "SALTSTR";
    const char *pwd = "password";

    char encoded[97] = {};

    // high-level API
    argon2id_hash_encoded(2, 1<<16, 2, pwd, sizeof(pwd), salt, sizeof(salt), 32, encoded, sizeof(encoded));

    printf("Encoded password: %s", encoded);
    int res =  argon2id_verify(encoded, pwd, sizeof(pwd));

    if (res == 0){
        printf("Verify password OK\n");
    } else {
        printf("Something went wrong while verify password\n");
    }

    return 0;
}

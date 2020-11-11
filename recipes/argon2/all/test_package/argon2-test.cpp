#include <iostream>
#include "argon2/argon2.h"

int main() {

    const char * salt = "SALTSTR";
    const char * pwd = "password";
    char encoded[97] = {};
    // high-level API
    argon2id_hash_encoded(2,1<<16,2,pwd,sizeof(pwd),salt,sizeof(salt),32,encoded,sizeof(encoded));

    std::cout << "Encoded password: " << encoded << std::endl;
    int res =  argon2id_verify(encoded, pwd, sizeof(pwd));

    if (res == 0){
        std::cout << "Verify password OK" << std::endl;
    } else {
        std::cout << "Something went wrong while verify password" << std::endl;
    }

    return 0;
}

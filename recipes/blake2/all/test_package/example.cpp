#include <blake2.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    char in[20] = "Conan";
    char out[20];
    char key[4] = "c++";

    int result = blake2(out, 20, in, 20, key, 3);

    printf("Hashing the string: %s \n", in);
    printf("Using key: %s \n", key);

    if (result == 0){
        printf("Hash: %s \n", out);
    }
    else
    {
        printf("Error during hashing \n");
    }

    return 0;
}
#include <tweetnacl.h>

/* Library needs external randombytes implemented */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

void randombytes(unsigned char * ptr,unsigned int length)
{
    int i;
    srand(time(NULL));

    for (i = 0; i < length; i++) {
        ptr[i] = (unsigned char)rand();
    }
}

typedef unsigned char u8;

#define PUB_KEY_LEN 32
#define PRIV_KEY_LEN 32
#define NONCE_LEN 24
#define PADDING_LEN 32

void hexdump(char * data, int len)
{
    int i;
    for (i = 0; i < len; i++) {
        printf("%02X", (u8)data[i]);
    }
    printf("\n");
}

int main() {
    char * padded_message;
    int padded_mlen;
    u8 sk[PRIV_KEY_LEN] = {0};
    u8 pk[PUB_KEY_LEN] = {0};
    u8 sk2[PRIV_KEY_LEN] = {0};
    u8 pk2[PUB_KEY_LEN] = {0};
    u8 nonce[NONCE_LEN] = {0};
    char message[] = "This is a cross-platform test of crypto_box/crypto_box_open in TweetNaCl.";
    u8 * ciphertext;
    char *decryptedmessage;

    // randomize nonce
    randombytes(nonce, NONCE_LEN);
    printf("Nonce: \n");
    hexdump((char*)nonce, NONCE_LEN);

    crypto_box_keypair(pk, sk);
    crypto_box_keypair(pk2, sk2);

    printf("Public key: \n");
    hexdump((char*)pk, PUB_KEY_LEN);
    printf("\nSecret key: \n");
    hexdump((char*)sk, PRIV_KEY_LEN);
    printf("Public key2: \n");
    hexdump((char*)pk2, PUB_KEY_LEN);
    printf("\nSecret key2: \n");
    hexdump((char*)sk2, PRIV_KEY_LEN);

    padded_mlen = strlen(message) + PADDING_LEN;
    padded_message = (char*) malloc(padded_mlen);
    memset(padded_message, 0, PADDING_LEN);
    memcpy(padded_message + PADDING_LEN, message, strlen(message));

    ciphertext = (u8*) malloc(padded_mlen);

    // we have a string so add 1 byte and NUL it so we can print it
    decryptedmessage = (char*) malloc(padded_mlen+1);
    decryptedmessage[padded_mlen] = '\0';

    printf("crypto_box returned: %d\n",crypto_box(ciphertext, (u8*)padded_message,  padded_mlen, nonce, pk2, sk));

    free(padded_message);

    printf("\nCipher text: \n");
    hexdump((char*)ciphertext, padded_mlen);
    printf("crypto_box_open returned: %d\n", crypto_box_open((u8*)decryptedmessage, ciphertext, padded_mlen, nonce, pk, sk2));
    free(ciphertext);
    printf("\nDecrypted text: \n");
    hexdump((char*)decryptedmessage, padded_mlen);

    printf("%s\n", decryptedmessage+32);

    // Check decrypted and original message
    if (strcmp(decryptedmessage+32, message) != 0) {
        free(decryptedmessage);
        fprintf(stderr, "Decrypted message doesn't match with original message");
        return 1;
    }

    free(decryptedmessage);
    return 0;
}

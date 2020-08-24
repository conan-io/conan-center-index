#include <est.h>
#include <stdio.h>

int main(void)
{
    /*
     * Initialize the library, including OpenSSL
     */
    est_apps_startup();

    char *key_data;
    EVP_PKEY *key;

    key_data = generate_private_RSA_key(2048, NULL /* no password_cb */);
    key = load_clear_private_key_PEM(key_data);

    if (!key)
    {
        printf("\nUnable to load newly created key from PEM file\n");
        exit(1);
    }
    memset(key_data, 0, strlen(key_data));
    free(key_data);
    key_data = NULL;
    EVP_PKEY_free(key);

    est_apps_shutdown();

    printf("\n");
    return 0;
}

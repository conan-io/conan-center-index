#include <est/est.h>
#include <stdio.h>

unsigned char *BIO_copy_data(BIO *out, int *data_lenp) {
    unsigned char *data, *tdata;
    int data_len;

    data_len = BIO_get_mem_data(out, &tdata);
    data = malloc(data_len+1);
    if (data) {
        memcpy(data, tdata, data_len);
	data[data_len]='\0';  // Make sure it's \0 terminated, in case used as string
	if (data_lenp) {
	    *data_lenp = data_len;
	}
    } else {
        printf("\nmalloc failed\n");
    }
    return data;
}


#define EST_PRIVATE_KEY_ENC EVP_aes_128_cbc()

char *generate_private_RSA_key (int key_size, pem_password_cb *cb)
{
    char *key_data = NULL;

    RSA *rsa = RSA_new();
    if (!rsa) {
        return NULL;
    }
    BIGNUM *bn = BN_new();
    if (!bn) {
        RSA_free(rsa);
        return NULL;
    }

    BN_set_word(bn, 0x10001);
    RSA_generate_key_ex(rsa, key_size, bn, NULL);

    do {
        BIO *out = BIO_new(BIO_s_mem());
        if (!out) {
            break;
        }
        PEM_write_bio_RSAPrivateKey(out, rsa, cb ? EST_PRIVATE_KEY_ENC : NULL, NULL, 0, cb, NULL);
        key_data = (char *)BIO_copy_data(out, NULL);
        BIO_free(out);
        if (key_data && !key_data[0]) {
            // happens if passphrase entered via STDIN does not verify or has less than 4 characters
            free(key_data);
            key_data = NULL;
        }
    } while (cb && !key_data);

    RSA_free(rsa);
    BN_free(bn);
    return (key_data);
}

EVP_PKEY *load_private_key (const unsigned char *key, int key_len, int format, pem_password_cb *cb)
{
    BIO *in = NULL;
    EVP_PKEY *pkey = NULL;

    if (key == NULL) {
        printf("\nNo key data provided\n");
        return NULL;
    }

    in = BIO_new_mem_buf((unsigned char *)key, key_len);
    if (in == NULL) {
        printf("\nUnable to open the provided key buffer\n");
        return (NULL);
    }

    switch (format) {
    case EST_FORMAT_PEM:
        pkey = PEM_read_bio_PrivateKey(in, NULL, cb, NULL);
        break;
    case EST_FORMAT_DER:
        pkey = d2i_PrivateKey_bio(in, NULL);
        break;
    default:
        printf("\nInvalid key format\n");
        break;
    }
    BIO_free(in);

    return (pkey);
}

#define load_clear_private_key_PEM(key) load_private_key((unsigned char*)(key),strlen(key),EST_FORMAT_PEM, NULL)

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

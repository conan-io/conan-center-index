#include <stdio.h>
#include <string.h>
#include <openssl/provider.h>
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/conf.h>

void print_openssl_error(void)
{
    unsigned long err;
    while ((err = ERR_get_error()) != 0)
        fprintf(stderr, "    OpenSSL: %s\n", ERR_error_string(err, NULL));
}

/*
 * Compute a digest of `input` using `algorithm`, fetched specifically from
 * `provider` (via a "provider=<name>" property query) so the test verifies
 * the named provider rather than whichever one happens to be active.
 * Returns 1 on success, 0 on failure.
 */
int test_digest(const char *provider, const char *algorithm, const char *input)
{
    char propq[64];
    snprintf(propq, sizeof(propq), "provider=%s", provider);

    EVP_MD *md = EVP_MD_fetch(NULL, algorithm, propq);
    if (!md) {
        print_openssl_error();
        return 0;
    }

    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int  digest_len = 0;
    int ok = 0;

    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (ctx != NULL
            && EVP_DigestInit_ex(ctx, md, NULL) == 1
            && EVP_DigestUpdate(ctx, input, strlen(input)) == 1
            && EVP_DigestFinal_ex(ctx, digest, &digest_len) == 1) {
        /* Report which provider actually served the implementation. */
        const OSSL_PROVIDER *served = EVP_MD_get0_provider(md);
        const char *served_name = served ? OSSL_PROVIDER_get0_name(served) : "?";

        printf("      digest(%s, \"%s\") [served by: %s] = ", algorithm, input, served_name);
        /* Print first 8 bytes as hex */
        for (unsigned int i = 0; i < digest_len && i < 8; i++)
            printf("%02x", digest[i]);
        printf("...  [PASS]\n");
        ok = 1;
    }

    EVP_MD_CTX_free(ctx);
    EVP_MD_free(md);
    return ok;
}

/*
 * Load `name` into the global context and report the result.
 *  - digest_alg: if non-NULL, exercise the provider with one digest
 *                (NULL for providers like "null" that expose no algorithms).
 *  - required:   if the load fails, report [FAIL]; otherwise a missing
 *                provider is reported as [SKIP]. A provider that is present
 *                but fails to initialise (an ERR_LIB_PROV error, e.g. a
 *                misconfigured fips) is always reported as [FAIL].
 *  - show_conf:  print the active OPENSSL_CONF (useful for fips diagnostics).
 */
void test_provider(const char *name, const char *digest_alg,
                   int required, int show_conf)
{
    printf("\n[Provider: %s]\n", name);

    if (show_conf) {
        char *conf_path = CONF_get1_default_config_file();
        printf("  OPENSSL_CONF: %s\n", conf_path ? conf_path : "(none)");
        OPENSSL_free(conf_path);
    }

    OSSL_PROVIDER *prov = OSSL_PROVIDER_load(NULL, name);
    if (!prov) {
        if (!required && ERR_GET_LIB(ERR_peek_error()) == ERR_LIB_PROV) {
            printf("  Load:  [FAIL] (%s provider present but failed to initialise)\n", name);
            printf("  Hint:  check OPENSSL_CONF / run 'openssl fipsinstall' for fips\n");
        } else if (!required) {
            printf("  Load:  [SKIP] (%s provider not installed)\n", name);
        } else {
            printf("  Load:  [FAIL]\n");
        }
        print_openssl_error();
        return;
    }
    printf("  Load:  [PASS]\n");

    if (digest_alg)
        test_digest(name, digest_alg, "hello");

    OSSL_PROVIDER_unload(prov);
}

int main(void)
{
    printf("OpenSSL version: %s\n", OpenSSL_version(OPENSSL_VERSION));

    /* provider     digest    required  show_conf */
    test_provider("default", "SHA256", 1, 0);  /* SHA256: from default provider */
    test_provider("legacy",  "MD4",    0, 0);  /* MD4: legacy-only digest */
    test_provider("fips",    "SHA256", 0, 1);  /* SHA256: FIPS-approved    */
    test_provider("null",    NULL,     1, 0);  /* exposes no algorithms    */

    printf("\nTest package successful\n");
    return 0;
}

#include <stdio.h>
#include <ldns/ldns.h>

static ldns_rr_list *rrset_from_str(const char *str)
{
    ldns_rr *rr = NULL;
    if (ldns_rr_new_frm_str(&rr, str, 0, NULL, NULL) != LDNS_STATUS_OK) {
        return NULL;
    }

    ldns_rr_list *rrset = ldns_rr_list_new();
    if (rrset == NULL) {
        ldns_rr_free(rr);
        return NULL;
    }

    if (!ldns_rr_list_push_rr(rrset, rr)) {
        ldns_rr_free(rr);
        ldns_rr_list_deep_free(rrset);
        return NULL;
    }

    return rrset;
}


int main(int argc, char *argv[])
{
    ldns_rr_list *data = rrset_from_str("nlnetlabs.nl. 240 IN AAAA 2a04:b900::1:0:0:10");
    ldns_rr_list *rrsigs = rrset_from_str("nlnetlabs.nl. 240 IN RRSIG AAAA 8 2 240 20210316015010 20210216015010 42393 nlnetlabs.nl. sZ24Gr6kcWVUMU+pFsoEiW+R7TeE2f3g9EcuIq3Rh+aA38ZslHIv41fFjN9KdfQOdivHlgZ+d6cvhJfXczaHHYRTpLdvkz6s/mbJ7z+NnvpJdQa7g1qWXD6f2rHyC0TjyV15divsK+aogSs/xXuRZfUlPxqe5Lrwtaxp0r471GU=");
    ldns_rr_list *dnskeys = rrset_from_str("nlnetlabs.nl. 3205 IN DNSKEY 256 3 8 AwEAAdR7XR95OaAN9Rz7TbtPalQ9guQk7zfxTHYNKhsiwTZA9z+F16nD0VeBlk7dNik3ETpT2GLAwr9sntG898JwurCDe353wHPvjZtMCdiTVp3cRCrjuCEvoFpmZNN82H0gaH/4v8mkv/QBDAkDSncYjz/FqHKAeYy3cMcjY6RyVweh");

    int ret = ldns_verify_notime(data, rrsigs, dnskeys, NULL);

    ldns_rr_list_deep_free(data);
    ldns_rr_list_deep_free(rrsigs);
    ldns_rr_list_deep_free(dnskeys);

    if (ret != LDNS_STATUS_OK) {
        printf("failed\n");
        return 1;
    }

    printf("ok\n");
    return 0;
}

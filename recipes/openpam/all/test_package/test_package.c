#include <stdio.h>
#include <stdlib.h>
#include <security/pam_types.h>
#include <security/openpam.h>
#include <security/pam_constants.h>
#include <security/pam_appl.h>


int main(void) {
    pam_handle_t* pamh;
    struct pam_conv pamc;
    const char *user;

    int rv = pam_start("yes", user, &pamc, &pamh);

    if(rv == PAM_SUCCESS) {
        pam_end(pamh, PAM_SUCCESS);
    }

    return EXIT_SUCCESS;
}


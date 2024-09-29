#include <security/pam_appl.h>
#include <security/pam_misc.h>

static struct pam_conv conv = {
    misc_conv,
    NULL
};

int main()
{
    pam_handle_t *pamh = NULL;
    const char *user = "";
    pam_start("check", user, &conv, &pamh);
}

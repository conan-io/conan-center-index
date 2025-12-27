#include <stdio.h>

#include <libnetconf2/netconf.h>
#include <libnetconf2/log.h>
#include <libnetconf2/session_client.h>

static void my_log_clb(NC_VERB_LEVEL level, const char *msg)
{
    printf("LOG[%d]: %s\n", level, msg);
}

int main()
{
    printf("libnetconf2 2.x test OK\n");

    /* Init client */
    nc_client_init();

    /* Set logger */
    nc_set_print_clb(my_log_clb);

    /* Simple API call check */
    const char *schema_path = nc_client_get_schema_searchpath();
    printf("Schema search path: %s\n", schema_path ? schema_path : "(null)");

    /* Cleanup */
    nc_client_destroy();

    return 0;
}

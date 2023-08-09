#include <mpd/connection.h>
#include <mpd/player.h>

#include <stddef.h>
#include <stdio.h>

int main()
{
    struct mpd_connection *conn = mpd_connection_new(NULL, 0, 0);

    if (conn == NULL) {
        fprintf(stderr, "Out of memory\n");
        return 1;
    }
    if (mpd_connection_get_error(conn) != MPD_ERROR_SUCCESS) {
        fprintf(stderr, "%s\n", mpd_connection_get_error_message(conn));
        mpd_connection_free(conn);
        return 0;
    }

    mpd_run_next(conn);
    mpd_connection_free(conn);

    return 0;
}

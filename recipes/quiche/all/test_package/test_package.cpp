#include <quiche.h>
#include <cstdio>

int main (int argc, char *argv[])
{
    auto q_config = quiche_config_new(QUICHE_PROTOCOL_VERSION);
    quiche_config_set_initial_max_data                      (q_config, 10000000);
    quiche_config_set_initial_max_stream_data_bidi_local    (q_config, 1000000);
    quiche_config_set_initial_max_stream_data_bidi_remote   (q_config, 1000000);
    quiche_config_set_initial_max_stream_data_uni           (q_config, 1000000);
    quiche_config_set_initial_max_streams_bidi              (q_config, 100);
    quiche_config_set_initial_max_streams_uni               (q_config, 100);
    quiche_config_set_disable_active_migration              (q_config, true);

    auto http3_config = quiche_h3_config_new();

    if (http3_config == nullptr) {
        fprintf(stderr, "failed to create HTTP/3 config\n");
        return 1;
    }

    quiche_h3_config_free(http3_config);
    quiche_config_free(q_config);

    printf ("WELL DONE\n");

    return 0;
}
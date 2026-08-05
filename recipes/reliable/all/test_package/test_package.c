#include <reliable.h>

#include <stdint.h>
#include <stdio.h>

/* reliable_endpoint_create requires non-NULL packet callbacks */

static void transmit_packet(void * context, uint64_t id, uint16_t sequence, uint8_t * packet_data, int packet_bytes)
{
    (void) context; (void) id; (void) sequence; (void) packet_data; (void) packet_bytes;
}

static int process_packet(void * context, uint64_t id, uint16_t sequence, uint8_t * packet_data, int packet_bytes)
{
    (void) context; (void) id; (void) sequence; (void) packet_data; (void) packet_bytes;
    return 1;
}

int main(void)
{
    struct reliable_config_t config;
    struct reliable_endpoint_t * endpoint;

    if (reliable_init() != RELIABLE_OK)
    {
        printf("reliable_init failed\n");
        return 1;
    }

    reliable_default_config(&config);
    config.transmit_packet_function = transmit_packet;
    config.process_packet_function = process_packet;

    endpoint = reliable_endpoint_create(&config, 100.0);
    if (endpoint == NULL)
    {
        printf("reliable_endpoint_create failed\n");
        return 1;
    }
    reliable_endpoint_destroy(endpoint);

    reliable_term();

    printf("reliable %s: endpoint created and destroyed\n", RELIABLE_VERSION_FULL);
    return 0;
}


#include <stdio.h>

#include <mqtt.h>

void publishCallback(void** unused, struct mqtt_response_publish* published)
{
    printf("Publish callback called\n");
}

int main()
{
    struct mqtt_client client;
    uint8_t sendBuffer[2048];
    uint8_t receiveBuffer[1024];

    printf("Initializing mqtt\n");

    // Second argument is native socket handle, which we will not use in the example
    mqtt_init(&client, 0,
              sendBuffer, sizeof(sendBuffer),
              receiveBuffer, sizeof(receiveBuffer),
              &publishCallback);

    printf("Done initializing mqtt\n");

    return 0;
}

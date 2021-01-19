#include <string>
#include "mqtt/async_client.h"
#include "mqtt/client.h"

const std::string SERVER_ADDRESS { "tcp://localhost:1883" };
const std::string CLIENT_ID { "consume" };


int main(int argc, char* argv[])
{
    mqtt::connect_options connOpts;
    connOpts.set_keep_alive_interval(20);
    connOpts.set_clean_session(true);

    mqtt::async_client cli_async(SERVER_ADDRESS, CLIENT_ID);
    mqtt::client cli(SERVER_ADDRESS, CLIENT_ID);

    return 0;
}


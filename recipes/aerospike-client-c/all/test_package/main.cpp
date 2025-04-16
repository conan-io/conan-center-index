#include <iostream>

#include <aerospike/aerospike.h>
#include <aerospike/as_event.h>
#include <aerospike/version.h>

int main()
{
    std::cout << "aerospike client version is " << AEROSPIKE_CLIENT_VERSION << std::endl;

    as_config config;
    as_config_init(&config);

    std::string host = "127.0.0.1";
    as_config_add_host(&config, host.c_str(), 3000);

    aerospike as;
    aerospike_init(&as, &config);

    as_error err;
    std::cout << "trying to connect to " << host << std::endl;
    if (aerospike_connect(&as, &err) != AEROSPIKE_OK)
    {
        std::cerr << "aerospike_connect() returned " << err.code << " (" << err.message << ")" << std::endl;
        as_event_close_loops();
        aerospike_destroy(&as);
    }

    return 0;
}

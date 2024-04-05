#include <iostream>

#include <aerospike/as_aerospike.h>

int main()
{
    as_aerospike as;
    as_aerospike_init(&as, nullptr, nullptr);
    as_aerospike_destroy(&as);
    return 0;
}

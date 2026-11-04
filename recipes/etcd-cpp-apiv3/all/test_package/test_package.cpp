#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "etcd/Client.hpp"

static const std::string etcd_url =
    etcdv3::detail::resolve_etcd_endpoints("http://127.0.0.1:2379");

int main()
{
    etcd::Client* etcd = etcd::Client::WithUser(etcd_url, "root", "root");
    return EXIT_SUCCESS;
}

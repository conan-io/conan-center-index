#include <cstdlib>
#include <iostream>

#include <mongocxx/client.hpp>
#include <mongocxx/instance.hpp>
#include <mongocxx/uri.hpp>

// Compilation check
#include <mongoc.h>
#include <bson.h>
#include <bsoncxx/json.hpp>

int main() {
    const mongocxx::instance instance_;  // This should be done only once.
    mongocxx::client client{mongocxx::uri{}};
    return EXIT_SUCCESS;
}

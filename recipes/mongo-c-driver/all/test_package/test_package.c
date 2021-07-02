#include <stdio.h>
#include <mongoc/mongoc.h>
#include <bson/bson.h>

int main() {
    printf("mongoc version: %s\n", mongoc_get_version());
    printf("bson version: %s\n", bson_get_version());

    return 0;
}

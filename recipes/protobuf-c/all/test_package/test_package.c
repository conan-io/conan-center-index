#include <stdio.h>
#include <stdlib.h>

#include "hero.pb-c.h"
#include "protobuf-c/protobuf-c.h"

int main()
{
    The__Hero hero;
    hero.name = "the_storyteller";

    printf("The hero's name is %s.\n", hero.name);
    printf("Protobuf-C version: %s\n", protobuf_c_version());

    return EXIT_SUCCESS;
}

#include <stdio.h>

#include "hero.pb-c.h"

int main()
{
    The__Hero hero;
    hero.name = "the_storyteller";

    printf("The hero's name is %s.\n", hero.name);

    return 0;
}

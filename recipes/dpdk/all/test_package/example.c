#include <stdio.h>

#include <rte_version.h>

int main(int argc, char** argv)
{
    puts(rte_version());
    return 0;
}

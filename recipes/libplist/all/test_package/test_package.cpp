#include <stdlib.h>
#include <stdio.h>
#include <plist/plist++.h>


int main(void) {
    auto node = new PList::Boolean(true);
    printf("node value: %d\n", node->GetValue());

    return EXIT_SUCCESS;
}

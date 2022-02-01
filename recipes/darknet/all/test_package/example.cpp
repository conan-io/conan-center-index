#include "darknet.h"

#include <iostream>

int main() {
    image image = make_image(2, 3, 1);
    free_image(image);
    return 0;
}

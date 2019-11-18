#include <iostream>
#include "darknet.h"

int main() {
    image image = make_image(2, 3, 1);
    free_image(image);
}

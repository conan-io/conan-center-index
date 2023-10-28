#include <iostream>

#include "ozz/base/log.h"
#include "ozz/base/io/stream.h"

int main()
{
    ozz::io::File file("test.ozz", "rb");

    if (!file.opened()) {
    }
}

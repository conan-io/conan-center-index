#include "ozz/base/log.h"
#include "ozz/base/io/stream.h"

#include <iostream>

int main()
{
    ozz::io::File file("test.ozz", "rb");

    if (!file.opened()) {
    }
}

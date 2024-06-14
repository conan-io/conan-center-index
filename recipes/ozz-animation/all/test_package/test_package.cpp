#include <iostream>

#include "ozz/base/log.h"
#include "ozz/base/io/stream.h"
#include "ozz/animation/runtime/animation.h"
#include "ozz/geometry/runtime/skinning_job.h"

int main()
{
    ozz::io::File file("test.ozz", "rb");

    if (!file.opened()) {
    }
}

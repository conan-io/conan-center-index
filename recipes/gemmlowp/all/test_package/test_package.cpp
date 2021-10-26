#include <cstdlib>
#include <iostream>
#define NOMINMAX
#include <public/gemmlowp.h>

int main()
{
    gemmlowp::GemmContext ctx;
    ctx.set_max_num_threads(1);
    return EXIT_SUCCESS;
}

/* This code is part of the tng binary trajectory format.
 *
 * Written by Magnus Lundborg
 * Copyright (c) 2012-2013, The GROMACS development team.
 * check out http://www.gromacs.org for more information.
 *
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the Revised BSD License.
 */

#include "tng/tng_io.h"

#ifdef USE_STD_INTTYPES_H
#include <inttypes.h>
#endif

#include <stdlib.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    tng_trajectory_t traj;
    if(tng_trajectory_init(&traj) != TNG_SUCCESS)
    {
        tng_trajectory_destroy(&traj);
        exit(1);
    }
    tng_trajectory_destroy(&traj);
    return 0;
}
